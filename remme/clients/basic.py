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

from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchHeader, BatchList
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction, TransactionHeader
)
from sawtooth_signing import CryptoFactory, ParseError, create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.setting_pb2 import Setting

from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import (
    hash512,
)
from remme.settings.helper import _make_settings_key
from remme.shared.stream import Stream
from remme.settings import PRIV_KEY_FILE
from remme.settings.default import load_toml_with_defaults
from remme.clients.router import Router
from remme.shared.exceptions import (
    ClientException,
)


LOGGER = logging.getLogger(__name__)


class BasicClient(Router):

    def __init__(self, family_handler=None, keyfile=None):
        config = load_toml_with_defaults('/config/remme-client-config.toml')['remme']['client']

        self.url = config['validator_rest_api_url']
        self._family_handler = family_handler() if callable(family_handler) else None
        self._stream = Stream(f'tcp://{ config["validator_ip"] }:{ config["validator_port"] }')

        if keyfile is None:
            keyfile = PRIV_KEY_FILE

        try:
            self._signer = self.get_signer_priv_key_from_file(keyfile)
        except ClientException as e:
            LOGGER.warning('Could not set up signer from file, detailed: %s', e)
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
    def set_priv_key_to_file(private_key, keyfile=None):
        if keyfile is None:
            keyfile = PRIV_KEY_FILE

        with open(keyfile, 'w') as fd:
            fd.write(private_key)

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

    def get_setting_value(self, key):
        setting = Setting()
        value = self.get_value(_make_settings_key(key))
        setting.ParseFromString(value)
        return setting.entries[0].value

    def get_value(self, address):
        result = self.fetch_state(address)
        return base64.b64decode(result['data'])

    def get_batch_status(self, batch_id):
        result = self.list_statuses([batch_id])
        return result['data'][0]['status']

    def get_signer(self):
        return self._signer

    def get_public_key(self):
        return self.get_signer().get_public_key().as_hex()

    def get_private_key(self):
        return self.get_signer()._private_key.as_hex()

    def get_signer_address(self):
        return self.make_address_from_data(self.get_public_key())

    def _get_prefix(self):
        return self._family_handler.namespaces[-1]

    def _get_address(self, pub_key):
        if len(pub_key) > 64:
            raise ClientException("Wrong pub_key size: {}".format(pub_key))
        prefix = self._get_prefix()
        return prefix + pub_key

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
        from remme.tp.account import AccountHandler

        return AccountHandler().make_address_from_data(self._signer.get_public_key().as_hex())

    def _send_transaction(self, method, data_pb, addresses_input, addresses_output):
        '''
           Signs and sends transaction to the network using rpc-api.

           :param str method: The method (defined in proto) for Transaction Processor to process the request.
           :param dict data: Dictionary that is required by TP to process the transaction.
           :param str addresses_input: list of addresses(keys) for which to get state.
           :param str addresses_output: list of addresses(keys) for which to save state.
        '''
        addresses_input_output = []
        addresses_input_output.extend(addresses_input)
        addresses_input_output.extend(addresses_output)
        addresses_input_output = list(set(addresses_input_output))

        payload = TransactionPayload()
        payload.method = method
        payload.data = data_pb.SerializeToString()

        # NOTE: Not all addresses could be in the same format
        # for address in addresses_input_output:
        #     if not is_address(address):
        #         raise ClientException('one of addresses_input_output {} is not an address'.format(addresses_input_output))

        batch_list = self.make_batch_list(payload, addresses_input, addresses_output)

        return self.submit_batches(batch_list.batches)

    def send_raw_transaction(self, transaction_pb):
        batch_list = self._sign_batch_list(self._signer, [transaction_pb])

        return self.submit_batches(batch_list.batches)

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
