import time
import base64
import logging
from unittest import mock

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from aiohttp_json_rpc.protocol import (
    encode_request,
)

from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader

from remme.shared.utils import hash512
from remme.shared.logging_setup import test
from remme.protos.account_pb2 import AccountMethod, TransferPayload, Account
from remme.protos.transaction_pb2 import TransactionPayload
from remme.clients.account import AccountClient
from remme.clients.pub_key import PubKeyClient
from remme.rpc_api.base import JsonRpc
from remme.rpc_api.account import get_balance
from remme.rpc_api.pkc import get_node_public_key
from remme.rpc_api.transaction import send_raw_transaction, get_batch_status

from tests.test_helper import HelperTestCase


LOGGER = logging.getLogger(__name__)


class RpcApiTestCase(AioHTTPTestCase, HelperTestCase):

    @staticmethod
    def create_raw_transaction_send_token_payload(pub_key_to, amount=1):
        client = AccountClient()
        signer = client._signer
        address = client.make_address_from_data(pub_key_to)
        node_address = client.get_user_address()

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
            inputs=[node_address, address],
            outputs=[node_address, address],
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

    async def get_application(self):
        app = web.Application()
        rpc = JsonRpc(loop=self.loop, max_workers=1)
        rpc.add_methods(
            ('', get_node_public_key),
            ('', send_raw_transaction),
            ('', get_balance),
            ('', get_batch_status),
        )
        app.router.add_route('POST', '/', rpc)
        return app

    async def create_rpc_request(self, method, params=None):
        if params is None:
            params = {}
        data = encode_request(method, id=int(time.time()), params=params)
        LOGGER.info(f'JSON RPC request payload: {data}')
        return await self.client.request(
            'POST', '/', data=data,
            headers={'Content-Type': 'application/json'}
        )

    @unittest_run_loop
    @test
    async def test_node_key_retrieve_info_and_it_ok(self):
        resp = await self.create_rpc_request('get_node_public_key')
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        pub_key = PubKeyClient().get_public_key()
        self.assertEqual(data['result'], pub_key)

    @mock.patch('remme.clients.basic.BasicClient.submit_batches',
                return_value={'data': 'c6bcb01255c1870a5d42fe2dde5e91fb0c5992ec0b49932cdab901539bf977f75bb7699c053cea16668ba732a7d597dd0c2b80f157f1a2514932078bb761de4b'})
    @unittest_run_loop
    @test
    async def test_valid_raw_transaction_send_to_the_node(self, req_mock):
        payload = self.create_raw_transaction_send_token_payload('03823c7a9e285246985089824f3aaa51fb8675d08d84b151833ca5febce37ad61e', 1)
        resp = await self.create_rpc_request(
            'send_raw_transaction',
            {'data': base64.b64encode(payload.SerializeToString()).decode('utf-8')}
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data['result'], 'c6bcb01255c1870a5d42fe2dde5e91fb0c5992ec0b49932cdab901539bf977f75bb7699c053cea16668ba732a7d597dd0c2b80f157f1a2514932078bb761de4b')

    @mock.patch('remme.clients.basic.BasicClient.fetch_state',
                return_value={'data': base64.b64encode(Account(balance=100).SerializeToString())})
    @mock.patch('remme.clients.basic.BasicClient._head_to_root',
                return_value=(None, 'some_root'))
    @unittest_run_loop
    @test
    async def test_get_token_balance(self, root_mock, fetch_state_mock):
        resp = await self.create_rpc_request(
            'get_balance',
            {'public_key': '03823c7a9e285246985089824f3aaa51fb8675d08d84b151833ca5febce37ad61a'}
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data['result'], 100)

    @mock.patch('remme.clients.basic.BasicClient.list_statuses',
                return_value={'data': [{'status': 'COMMITTED'}]})
    @unittest_run_loop
    @test
    async def test_check_batch_status(self, batch_status_mock):
        resp = await self.create_rpc_request(
            'get_batch_status',
            {'id': '3936f0fa13d008c2b00d04013dfa5e5359fccc117e4c47b1416ee24e115ac08b08707be3b3ce6956ca3d789d245ff0dddf7a39bc2b2f4210ffe81ebd0244c014'}
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data['result'], 'COMMITTED')
