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
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.transaction_pb2 import EmptyPayload
from remme.protos.consensus_account_pb2 import ConsensusAccount
from remme.protos.account_pb2 import Account
from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeState,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
    SetBetPayload,
)

from remme.shared.forms import (
    NodeAccountInternalTransferPayloadForm,
    ProtoForm,
    NodeAccountGenesisForm,
    SetBetPayloadForm,
    ProtoForm,
)
from remme.shared.utils import client_to_real_amount

from remme.settings import (
    SETTINGS_MINIMUM_STAKE,
    SETTINGS_GENESIS_OWNERS,
    NODE_STATE_ADDRESS,
    ZERO_ADDRESS,
)

from remme.settings.helper import _get_setting_value
from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'bet'
FAMILY_VERSIONS = ['0.1']


class BetHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            NodeAccountMethod.DO_BET: {
                PB_CLASS: EmptyPayload,
                PROCESSOR: self._do_bet,
                VALIDATOR: ProtoForm,
            },
        }

    def _do_bet(self, context, public_key, pb_payload):
        from .consensus_account import ConsensusAccountHandler
        from .node_account import NodeAccountHandler

        genesis_owners = _get_setting_value(context, SETTINGS_GENESIS_OWNERS)
        genesis_owners = genesis_owners.split(',') \
            if genesis_owners is not None else []

        # NOTE: Dirty hack for test
        if public_key in genesis_owners:
            LOGGER.info("Genesis node, skipping bet")
            return {}

        signer_node_address = NodeAccountHandler().make_address_from_data(public_key)
        node_account, consensus_account, zero_account = get_multiple_data(context, [
            (signer_node_address, NodeAccount),
            (ConsensusAccountHandler.CONSENSUS_ADDRESS, ConsensusAccount),
            (ZERO_ADDRESS, Account),
        ])

        if not node_account:
            raise InvalidTransaction('Node account not found.')

        if not consensus_account:
            raise InvalidTransaction('Consensus account not found.')

        if not zero_account:
            zero_account = Account()

        # TODO: Uncomment in the future
        # block_cost = consensus_account.block_cost
        block_cost = zero_account.balance

        bet = 0
        if node_account.min:
            bet = block_cost
        elif node_account.fixed_amount:
            bet = node_account.fixed_amount * block_cost
        elif node_account.max:
            bet = 9 * block_cost

        consensus_account.bets[signer_node_address] = bet
        node_account.balance -= bet

        LOGGER.info(f"Doing bet of size {bet}")

        return {
            ConsensusAccountHandler.CONSENSUS_ADDRESS: consensus_account,
            signer_node_address: node_account,
        }
