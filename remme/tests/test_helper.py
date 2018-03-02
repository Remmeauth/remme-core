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

from sawtooth_processor_test.transaction_processor_test_case \
    import TransactionProcessorTestCase
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from remme.certificate.certificate_handler import CertificateHandler
from remme.protos.transaction_pb2 import TransactionPayload
from remme.token.token_handler import TokenHandler

HANDLERS = [TokenHandler, CertificateHandler]


class HelperTestCase(TransactionProcessorTestCase):
    @classmethod
    def setUpClass(cls, handler):
        super().setUpClass()
        cls.handler = handler()

        account_signer1 = cls.get_new_signer()
        cls.account_address1 = cls.handler.make_address_from_data(account_signer1.get_public_key().as_hex())
        account_signer2 = cls.get_new_signer()
        cls.account_address2 = cls.handler.make_address_from_data(account_signer2.get_public_key().as_hex())

        cls._factory = cls.handler.get_message_factory(account_signer1)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.validator.close()
        except AttributeError:
            pass

    @classmethod
    def get_new_signer(cls):
        context = create_context('secp256k1')
        return CryptoFactory(context).new_signer(
            context.new_random_private_key())

    def expect_tps(self):
        for handler_class in HANDLERS[1:2]:
            print('expect')
            self.validator.expect(handler_class().get_message_factory(self.get_new_signer()).create_tp_register())
            print('success')



    def send_transaction(self, method, pb_data, address_access_list):
        payload_pb = TransactionPayload()
        payload_pb.method = method
        payload_pb.data = pb_data.SerializeToString()
        self.validator.send(
            self._factory.create_tp_process_request(payload_pb.SerializeToString(), address_access_list, address_access_list, [])
        )

    def expect_get(self, key_value):
        received = self.validator.expect(
            self._factory.create_get_request([address for address, _ in key_value.items()]))
        self.validator.respond(
            self._factory.create_get_response(key_value),
            received)

    def expect_set(self, key_value):
        received = self.validator.expect(
            self._factory.create_set_request([address for address, _ in key_value.items()]))
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
