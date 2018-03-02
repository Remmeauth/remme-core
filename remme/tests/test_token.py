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

from protobuf_to_dict import protobuf_to_dict

from remme.protos.token_pb2 import TokenMethod, GenesisStatus, Account, TransferPayload
from remme.tests.test_helper import HelperTestCase
from remme.token.token_client import TokenClient
from remme.token.token_handler import ZERO_ADDRESS, TokenHandler


# TODO update tests to correspond the new API
class TokenTestCase(HelperTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(TokenHandler)
        cls.token_client = TokenClient()

    def test_empty_genesis(self):
        TOTAL_SUPPLY = 10000
        zero_address = self.handler.make_address(ZERO_ADDRESS)

        self.send_transaction(TokenMethod.GENESIS, self.token_client.get_genesis_payload(TOTAL_SUPPLY),
                              self.account_address1)

        self.expect_get({self.account_address1: None})
        self.expect_get({zero_address: None})

        genesis_status = GenesisStatus()
        genesis_status.status = True
        account = Account()
        account.balance = TOTAL_SUPPLY

        self.expect_set({
            self.account_address1: account,
            zero_address: genesis_status
        })

    def test_transfer(self):
        pass
        # TODO: new test logic
