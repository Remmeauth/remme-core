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
from .context import remme_transaction_processor
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory


class HelperTestCase(TransactionProcessorTestCase):
    @classmethod
    def setUpClass(cls, factory):
        super().setUpClass()
        cls._factory = factory

    def _dumps(self, obj):
        return cbor.dumps(obj, sort_keys=True)

    def _loads(self, data):
        return cbor.loads(data)

    def get_new_signer(self):
        context = create_context('secp256k1')
        return CryptoFactory(context).new_signer(
            context.new_random_private_key())

    def make_address(self, appendix):
        return self._prefix + appendix

    def expect_ok(self):
        self.expect_tp_response('OK')

    def send_transaction(self, method, data, address_access_list):
        payload = self._dumps({'method': method, 'data': data})
        self._factory.create_transaction(payload, address_access_list, address_access_list, [])

    def expect_ok(self):
        self.expect_tp_response('OK')

    def expect_invalid(self):
        self.expect_tp_response('INVALID_TRANSACTION')

    def expect_tp_response(self, response):
        self.validator.expect(
            self.player_1.create_tp_response(
                response))
