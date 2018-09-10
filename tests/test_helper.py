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
import os
import logging

from contextlib import suppress

from unittest import TestCase, mock

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from sawtooth_processor_test.mock_validator import MockValidator

from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import AttrDict
from remme.clients.basic import BasicClient
from remme.clients.account import AccountClient
from remme.tp.account import AccountHandler, EMIT_EVENT

from remme.tp.__main__ import TP_HANDLERS
from remme.tp.basic import get_event_attributes

LOGGER = logging.getLogger(__name__)


class RemmeMockValidator(MockValidator):

    def wait_for_ready(self):
        pass


class HelperTestCase(TestCase):
    @classmethod
    def setUpClass(cls, handler, client_class=None):
        url = os.getenv('TEST_BIND', 'tcp://127.0.0.1:4004')

        cls.validator = RemmeMockValidator()

        cls.validator.listen(url)

        for item in TP_HANDLERS:
            if not cls.validator.register_processor():
                raise Exception('Failed to register processor')

        cls.factory = None

        cls._zmq_patcher = mock.patch('remme.clients.basic.Stream',
                                      return_value=cls.validator)
        cls._zmq_patcher_obj = cls._zmq_patcher.start()

        cls.handler = handler()
        cls.client_class = client_class

        cls._pk_patcher = mock.patch('remme.clients.basic.BasicClient.get_signer_priv_key_from_file',
                                     return_value=BasicClient.generate_signer())
        cls._pk_patcher_obj = cls._pk_patcher.start()

        # generate token account addresses
        cls.account_signer1 = cls.get_new_signer()
        cls.account_address1 = AccountHandler().make_address_from_data(cls.account_signer1.get_public_key().as_hex())
        cls.account_signer2 = cls.get_new_signer()
        cls.account_address2 = AccountHandler().make_address_from_data(cls.account_signer2.get_public_key().as_hex())

        cls._factory = cls.handler.get_message_factory(cls.account_signer1)

    @classmethod
    def tearDownClass(cls):
        with suppress(AttributeError):
            cls.validator.close()
        cls._zmq_patcher.stop()
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

        payload_pb = TransactionPayload()
        payload_pb.method = method
        payload_pb.data = pb_data.SerializeToString()

        tp_process_request = factory.create_tp_process_request(payload_pb.SerializeToString(), address_access_list,
                                                               address_access_list, [])
        self.validator.send(
            tp_process_request
        )

        return tp_process_request.signature

    def expect_event(self, signature, event_type, updated_state):
        received = self.validator.expect(
            self._factory.create_add_event_request(event_type, get_event_attributes(updated_state, signature)))
        LOGGER.info('expect_event')

        self.validator.respond(
            self._factory.create_add_event_response(),
            received)

    def expect_get(self, key_value):
        LOGGER.info('expect_get: {}'.format(key_value))
        received = self.validator.expect(
            self._factory.create_get_request([address for address, _ in key_value.items()]))
        LOGGER.info('expect_get create_get_response')

        resp_dict = {}
        for key, value in key_value.items():
            if hasattr(value, 'SerializeToString'):
                resp_dict[key] = value.SerializeToString()
            elif value is None:
                resp_dict[key] = None
            else:
                resp_dict[key] = str(value).encode()

        self.validator.respond(
            self._factory.create_get_response(resp_dict), received)

    def expect_set(self, signature, method, key_value):
        received = self.validator.expect(
            self._factory.create_set_request({key: value_pb.SerializeToString()
                                              if value_pb is not None else None
                                              for key, value_pb in key_value.items()}))

        print('sending set response...')
        self.validator.respond(
            self._factory.create_set_response(key_value), received)

        processor = self.handler.get_state_processor()[method]
        event_type = processor.get(EMIT_EVENT, None)
        if event_type:
            self.expect_event(signature, event_type, key_value)

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
        self.expect_get({address1: AccountClient.get_account_model(amount1),
                         address2: AccountClient.get_account_model(amount2)})

        return {
            address1: AccountClient.get_account_model(amount1 - value),
            address2: AccountClient.get_account_model(amount2 + value)
        }
