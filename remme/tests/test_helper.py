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
from sawtooth_processor_test.mock_validator import MockValidator
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
import cbor


class HelperTestCase(TransactionProcessorTestCase):
    @classmethod
    def setUpClass(cls, factory, pb_payload_class):
        super().setUpClass()
        url = 'tcp://eth0:4004'

        cls.validator = MockValidator()
        cls.validator.listen(url)
        cls._factory = factory
        cls._pb_payload_class = pb_payload_class

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

    def _dumps(self, obj):
        return cbor.dumps(obj, sort_keys=True)

    def send_transaction(self, method, pb_data, address_access_list):
        payload_pb = self._pb_payload_class()
        payload_pb.method = method
        payload_pb.data = pb_data.SerializeToString()
        self.validator.send(
            self._factory.create_transaction(payload_pb.SerializeToString(), address_access_list, address_access_list, [])
        )

    def expect_ok(self):
        self.expect_tp_response('OK')

    def expect_invalid(self):
        self.expect_tp_response('INVALID_TRANSACTION')

    def expect_tp_response(self, response):
        self.validator.expect(
            self._factory.create_tp_response(
                response))
