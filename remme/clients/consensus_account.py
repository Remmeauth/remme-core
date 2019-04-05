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

from remme.protos.consensus_account_pb2 import (
    ConsensusAccount,
    ConsensusAccountMethod,
)
from remme.protos.transaction_pb2 import EmptyPayload
from remme.clients.basic import BasicClient
from remme.tp.consensus_account import ConsensusAccountHandler
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings.helper import _make_settings_key
from remme.settings import SETTINGS_GENESIS_OWNERS
from remme.shared.utils import real_to_client_amount


class ConsensusAccountClient(BasicClient):

    CONSENSUS_ACCOUNT_GENESIS_BATCH = '/genesis/batch/consensus-proposal.batch'

    def __init__(self):
        super().__init__(ConsensusAccountHandler)

    @classmethod
    def get_empty_payload(self):
        payload = EmptyPayload()
        return payload

    async def get_account(self, address):
        account = ConsensusAccount()
        raw_account = await self.get_value(address)
        account.ParseFromString(raw_account)
        return account

    def generate_genesis_batches(self):
        self._generate_genesis_consensus_account_batch()

    def _generate_genesis_consensus_account_batch(self):
        addresses_input = [
            self._family_handler.CONSENSUS_ADDRESS,
            _make_settings_key(SETTINGS_GENESIS_OWNERS)
        ]
        addresses_output = [
            self._family_handler.CONSENSUS_ADDRESS
        ]

        payload = TransactionPayload()
        payload.method = ConsensusAccountMethod.GENESIS
        payload.data = self.get_empty_payload().SerializeToString()

        return self._write_batch_to_file(self.CONSENSUS_ACCOUNT_GENESIS_BATCH,
                                         payload,
                                         addresses_input,
                                         addresses_output)