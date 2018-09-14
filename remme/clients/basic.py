# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
import logging
import base64
import time
import json
from contextlib import suppress

import requests
from google.protobuf.message import DecodeError
from sawtooth_sdk.protobuf.block_pb2 import BlockHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchHeader, BatchList
from sawtooth_sdk.protobuf.client_list_control_pb2 import ClientPagingControls
from sawtooth_sdk.protobuf.client_block_pb2 import (
    ClientBlockListResponse, ClientBlockListRequest
)
from sawtooth_sdk.protobuf.client_state_pb2 import (
    ClientStateGetResponse, ClientStateGetRequest
)
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction, TransactionHeader
)
from sawtooth_sdk.protobuf.client_peers_pb2 import (
    ClientPeersGetRequest, ClientPeersGetResponse
)
from sawtooth_sdk.protobuf.client_batch_submit_pb2 import (
    ClientBatchSubmitRequest, ClientBatchSubmitResponse,
    ClientBatchStatusRequest, ClientBatchStatusResponse,
)
from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.messaging.exceptions import ValidatorConnectionError
from sawtooth_signing import CryptoFactory, ParseError, create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.exceptions import ClientException, KeyNotFound
from remme.shared.utils import hash512, get_batch_id, message_to_dict
from remme.shared.stream import Stream
from remme.tp.account import AccountHandler, is_address
from remme.settings import PRIV_KEY_FILE
from remme.settings.default import load_toml_with_defaults


LOGGER = logging.getLogger(__name__)


class BasicClient:
    def __init__(self, family_handler=None, test_helper=None, keyfile=None):
        config = load_toml_with_defaults('/config/remme-client-config.toml')['remme']['client']

        self.url = config['validator_rest_api_url']
        self._family_handler = family_handler() if callable(family_handler) else None
        self.test_helper = test_helper
        self._stream = Stream(f'tcp://{ config["validator_ip"] }:{ config["validator_port"] }')

        if keyfile is None:
            keyfile = PRIV_KEY_FILE

        try:
            self._signer = self.get_signer_priv_key_from_file(keyfile)
        except ClientException as e:
            LOGGER.warn('Could not set up signer from file, detailed: %s', e)
            self._signer = self.generate_signer(keyfile)

    @staticmethod
    def get_signer_priv_key_from_file(keyfile):
        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise ClientException(
                'Failed to read private key: {}'.format(str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise ClientException(
                'Unable to load private key: {}'.format(str(e)))

        context = create_context('secp256k1')
        return CryptoFactory(context).new_signer(private_key)

    @staticmethod
    def generate_signer(keyfile=None):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        if keyfile:
            try:
                with open(keyfile, 'w') as fd:
                    fd.write(private_key.as_hex())
            except OSError as err:
                raise ClientException(f'Failed to write private key: {err}')
        return CryptoFactory(context).new_signer(private_key)

    def make_address(self, suffix):
        return self._family_handler.make_address(suffix)

    def make_address_from_data(self, data):
        return self._family_handler.make_address_from_data(data)

    def is_address(self, address):
        return self._family_handler.is_address(address)

    def get_value(self, address):
        result = self._send_request(f"state/{address}",
                                    conn_protocol='socket')
        return base64.b64decode(result['data'])

    def get_batch(self, batch_id):
        result = self._send_request(f"batch_statuses?id={batch_id}",
                                    conn_protocol='socket')
        return result['data'][0]

    def get_signer(self):
        return self._signer

    def get_public_key(self):
        return self.get_signer().get_public_key().as_hex()

    def get_signer_address(self):
        return self.make_address_from_data(self.get_public_key())

    def _get_prefix(self):
        return self._family_handler.namespaces[-1]

    def _get_address(self, pub_key):
        if len(pub_key) > 64:
            raise ClientException("Wrong pub_key size: {}".format(pub_key))
        prefix = self._get_prefix()
        return prefix + pub_key

    def _send_request(self, suffix, data=None, conn_protocol='text', **kwargs):
        if conn_protocol == 'text':
            return self._text_request(suffix, data, **kwargs)
        elif conn_protocol == 'socket':
            return self._socket_request(suffix, data, **kwargs)
        raise ClientException(
            'Unsupported connection protocol "%s"' % conn_protocol)

    def _text_request(self, suffix, data=None, content_type=None):
        url = f"{self.url}/{suffix}"

        if not url.startswith("http://"):
            url = f"http://{url}"

        headers = {}
        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                with suppress(AttributeError):
                    data = data.SerializeToString()

                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise KeyNotFound("404")

            elif not result.ok:
                raise ClientException("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise ClientException(
                'Failed to connect to REST API: {}'.format(err))

        return json.loads(result.text)

    def _socket_request(self, suffix, data=None):
        if suffix == 'batches':
            return self.submit_batches({'batches': data.batches})
        elif 'batch_statuses?id=' in suffix:
            _, batch_id = suffix.split('?id=')
            return self.get_batch_statuses({'batch_ids': [batch_id]})
        elif 'state/' in suffix:
            _, address = suffix.split('/')
            _, root = self.get_root_block()
            return self.fetch_state({'state_root': root, 'address': address})
        else:
            raise ClientException('Suffix "%s" not supported' % suffix)

    def _handle_response(self, msg_type, resp_proto, req):
        self._stream.wait_for_ready()
        future = self._stream.send(
            message_type=msg_type,
            content=req.SerializeToString())

        resp = resp_proto()
        try:
            resp.ParseFromString(future.result().content)
        except (DecodeError, AttributeError):
            raise ClientException(
                'Failed to parse "content" string from validator')
        except ValidatorConnectionError as vce:
            LOGGER.error('Error: %s' % vce)
            raise ClientException(
                'Failed with ZMQ interaction: {0}'.format(vce))

        data = message_to_dict(resp)

        # NOTE: Not all protos have this status
        with suppress(AttributeError):
            if resp.status == resp_proto.NO_RESOURCE:
                raise KeyNotFound("404")

        if resp.status != resp_proto.OK:
            raise ClientException("Error: %s" % data)

        return data

    def fetch_peers(self):
        resp = self._handle_response(Message.CLIENT_PEERS_GET_REQUEST,
                                     ClientPeersGetResponse,
                                     ClientPeersGetRequest())
        return {'data': resp['peers']}

    def get_root_block(self):
        resp = self._handle_response(Message.CLIENT_BLOCK_LIST_REQUEST,
                                     ClientBlockListResponse,
                                     ClientBlockListRequest(
                                         paging=ClientPagingControls(limit=1)))
        block = resp['blocks'][0]
        header = BlockHeader()
        try:
            header_bytes = base64.b64decode(block['header'])
            header.ParseFromString(header_bytes)
        except (KeyError, TypeError, ValueError, DecodeError):
            header = block.get('header', None)
            LOGGER.error(
                'The validator sent a resource with %s %s',
                'a missing header' if header is None else 'an invalid header:',
                header or '')
            raise ClientException()

        block['header'] = message_to_dict(header)

        return (
            block['header_signature'],
            block['header']['state_root_hash'],
        )

    def submit_batches(self, data):
        self._handle_response(Message.CLIENT_BATCH_SUBMIT_REQUEST,
                              ClientBatchSubmitResponse,
                              ClientBatchSubmitRequest(batches=data['batches']))

        id_string = ','.join(b.header_signature for b in data['batches'])
        link = f"{self.url}/batch_statuses?id={id_string}"
        return {'link': link}

    def fetch_state(self, data):
        resp = self._handle_response(Message.CLIENT_STATE_GET_REQUEST,
                                     ClientStateGetResponse,
                                     ClientStateGetRequest(state_root=data['state_root'],
                                                           address=data['address']))

        return {'data': resp['value']}

    def get_batch_statuses(self, data):
        resp = self._handle_response(Message.CLIENT_BATCH_STATUS_REQUEST,
                                     ClientBatchStatusResponse,
                                     ClientBatchStatusRequest(batch_ids=data['batch_ids']))
        return {'data': resp['batch_statuses']}

    def make_batch_list(self, payload_pb, addresses_input, addresses_output):
        payload = payload_pb.SerializeToString()
        signer = self._signer
        header = TransactionHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            family_name=self._family_handler.family_name,
            family_version=self._family_handler.family_versions[-1],
            inputs=addresses_input,
            outputs=addresses_output,
            dependencies=[],
            payload_sha512=hash512(payload),
            batcher_public_key=signer.get_public_key().as_hex(),
            nonce=time.time().hex().encode()
        ).SerializeToString()

        signature = signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        return self._sign_batch_list(signer, [transaction])

    def set_signer(self, new_signer):
        self._signer = new_signer

    def get_user_address(self):
        return AccountHandler().make_address_from_data(self._signer.get_public_key().as_hex())

    def _send_transaction(self, method, data_pb, addresses_input, addresses_output):
        '''
           Signs and sends transaction to the network using rest-api.

           :param str method: The method (defined in proto) for Transaction Processor to process the request.
           :param dict data: Dictionary that is required by TP to process the transaction.
           :param str addresses_input: list of addresses(keys) for which to get state.
           :param str addresses_output: list of addresses(keys) for which to save state.
        '''
        addresses_input_output = []
        addresses_input_output.extend(addresses_input)
        addresses_input_output.extend(addresses_output)
        addresses_input_output = list(set(addresses_input_output))
        # forward transaction to test helper
        if self.test_helper:
            self.test_helper.send_transaction(method, data_pb, addresses_input_output)
            return

        payload = TransactionPayload()
        payload.method = method
        payload.data = data_pb.SerializeToString()

        for address in addresses_input_output:
            if not is_address(address):
                raise ClientException('one of addresses_input_output {} is not an address'.format(addresses_input_output))

        batch_list = self.make_batch_list(payload, addresses_input, addresses_output)

        return get_batch_id(self._send_request('batches', batch_list, 'socket'))

    def _send_raw_transaction(self, transaction_pb):
        batch_list = self._sign_batch_list(self._signer, [transaction_pb])

        return get_batch_id(self._send_request('batches', batch_list, 'socket'))

    def _sign_batch_list(self, signer, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])
