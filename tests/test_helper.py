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
# ------------------------------------------------------------------------
import logging

from unittest import mock

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import AttrDict
from remme.clients.basic import BasicClient
from tests.tp_test_case import TransactionProcessorTestCase
from remme.clients.account import AccountClient
from remme.tp.account import AccountHandler

LOGGER = logging.getLogger(__name__)


class HelperTestCase(TransactionProcessorTestCase):
    @classmethod
    def setUpClass(cls, handler, client_class=None):
        super().setUpClass()
        cls.handler = handler
        cls.client_class = client_class

        cls._pk_patcher = mock.patch('remme.clients.basic.BasicClient.get_signer_priv_key_from_file',
                                     return_value=BasicClient.generate_signer())
        cls._pk_patcher_obj = cls._pk_patcher.start()

        # generate token account addresses
        cls.account_signer1 = cls.get_new_signer()
        cls.account_address1 = AccountHandler.make_address_from_data(cls.account_signer1.get_public_key().as_hex())
        cls.account_signer2 = cls.get_new_signer()
        cls.account_address2 = AccountHandler.make_address_from_data(cls.account_signer2.get_public_key().as_hex())

        cls._factory = cls.handler.get_message_factory(cls.account_signer1)


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._pk_patcher.stop()

    @classmethod
    def get_new_signer(cls):
        context = create_context('secp256k1')
        return CryptoFactory(context).new_signer(
            context.new_random_private_key())

    def get_context(self):
        context = AttrDict()
        context.client = self.client_class(test_helper=self)
        context.client.set_signer(self.account_signer1)

        return context

    def send_transaction(self, method, pb_data, address_access_list, account_signer=None):
        factory = self._factory
        if account_signer is not None:
            factory = self.handler.get_message_factory(account_signer)
        LOGGER.info('send_transaction')
        payload_pb = TransactionPayload()
        payload_pb.method = method
        payload_pb.data = pb_data.SerializeToString()
        self.validator.send(
            factory.create_tp_process_request(payload_pb.SerializeToString(), address_access_list, address_access_list, [])
        )

    def expect_get(self, key_value):
        LOGGER.info('expect_get: {}'.format(key_value))
        received = self.validator.expect(
            self._factory.create_get_request([address for address, _ in key_value.items()]))
        LOGGER.info('expect_get create_get_response')

        self.validator.respond(
            self._factory.create_get_response(
                {key: value.SerializeToString() if hasattr(value, 'SerializeToString') else str(value).encode()
                        if value else None for key, value in key_value.items()
                }),
            received)

    def expect_set(self, key_value):
        received = self.validator.expect(
            self._factory.create_set_request({key: value_pb.SerializeToString()
                                              for key, value_pb in key_value.items()}))

        print('sending set response...')
        self.validator.respond(
            self._factory.create_set_response(key_value), received)

    def _expect_tp_response(self, response):
        self.validator.expect(
            self._factory.create_tp_response(response))

    def expect_ok(self):
        self._expect_tp_response('OK')

    def expect_invalid_transaction(self):
        self._expect_tp_response("INVALID_TRANSACTION")

    def expect_internal_error(self):
        self._expect_tp_response("INTERNAL_ERROR")

    # a short term solution
    def transfer(self, address1, amount1, address2, amount2, value):
        self.expect_get({address1: AccountClient.get_account_model(amount1)})
        self.expect_get({address2: AccountClient.get_account_model(amount2)})

        return {
            address1: AccountClient.get_account_model(amount1 - value),
            address2: AccountClient.get_account_model(amount2 + value)
        }
