import time
import json
import base64
from pkg_resources import resource_filename
from unittest import mock

import connexion

from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader


from remme.rest_api.api_methods_switcher import RestMethodsSwitcherResolver
from remme.shared.utils import hash512
from remme.shared.logging import test
from remme.protos.account_pb2 import AccountMethod, TransferPayload
from remme.protos.transaction_pb2 import TransactionPayload
from remme.account.client import AccountClient
from remme.account.handler import AccountHandler
from remme.tests.test_helper import HelperTestCase


class RestApiTestCase(HelperTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(AccountHandler, AccountClient)
        flask_app = connexion.FlaskApp('remme.rest_api')
        flask_app.add_api(resource_filename('remme.rest_api', 'openapi.yml'),
                          resolver=RestMethodsSwitcherResolver('remme.rest_api'))
        cls.client = flask_app.app.test_client()

    @classmethod
    def create_raw_transaction_send_token_payload(cls, pub_key_to, amount=1):
        client = cls.client_class()
        signer = client._signer
        address = client.make_address_from_data(pub_key_to)

        transfer = TransferPayload()
        transfer.address_to = address
        transfer.value = amount

        tr = TransactionPayload()
        tr.method = AccountMethod.TRANSFER
        tr.data = transfer.SerializeToString()

        payload = tr.SerializeToString()

        header = TransactionHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            family_name=client._family_handler.family_name,
            family_version=client._family_handler.family_versions[-1],
            inputs=[address],
            outputs=[address],
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
        return transaction

    @test
    def test_node_key_retrieve_info_and_it_ok(self):
        response = self.client.get('/api/v1/node_key')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pubkey' in response.get_json())

    @test
    @mock.patch('remme.shared.basic_client.BasicClient._send_request',
                return_value=json.dumps({'link': 'http://rest-api:8080/batch_statuses?id=c6bcb01255c1870a5d42fe2dde5e91fb0c5992ec0b49932cdab901539bf977f75bb7699c053cea16668ba732a7d597dd0c2b80f157f1a2514932078bb761de4b'}))
    def test_valid_raw_transaction_send_to_the_node(self, req_mock):
        payload = self.create_raw_transaction_send_token_payload('03823c7a9e285246985089824f3aaa51fb8675d08d84b151833ca5febce37ad61e', 1)
        response = self.client.post('/api/v1/transaction',
                                    data=json.dumps({
                                        'transaction': base64.b64encode(payload.SerializeToString()).decode('utf-8')
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200, 'Error: %s' % response.get_data())
        self.assertTrue('batch_id' in response.get_json())

    @test
    @mock.patch('remme.shared.basic_client.BasicClient._send_request',
                return_value=json.dumps({'link': 'http://rest-api:8080/batch_statuses?id=c6bcb01255c1870a5d42fe2dde5e91fb0c5992ec0b49932cdab901539bf977f75bb7699c053cea16668ba732a7d597dd0c2b80f157f1a2514932078bb761de4b'}))
    def test_token_send(self, req_mock):
        response = self.client.post('/api/v1/token',
                                    data=json.dumps({
                                        "pub_key_to": "03823c7a9e285246985089824f3aaa51fb8675d08d84b151833ca5febce37ad61e",
                                        "amount": 1
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200, 'Error: %s' % response.get_data())
        self.assertTrue('batch_id' in response.get_json())
