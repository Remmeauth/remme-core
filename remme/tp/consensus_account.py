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
from remme.protos.account_pb2 import Account
from remme.protos.node_account_pb2 import NodeAccount
from remme.protos.consensus_account_pb2 import (
    ConsensusAccount,
    ConsensusAccountMethod,
)
from remme.settings import (
    SETTINGS_BLOCKCHAIN_TAX,
    SETTINGS_MIN_SHARE,
    SETTINGS_COMMITTEE_SIZE,
    SETTINGS_MINIMUM_STAKE,
    ZERO_ADDRESS,
)
from remme.settings.helper import _get_setting_value
from remme.shared.utils import hash512
from remme.shared.forms import ProtoForm
from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)
from .account import AccountHandler
from .node_account import NodeAccountHandler


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'consensus_account'
FAMILY_VERSIONS = ['0.1']


class ConsensusAccountHandler(BasicHandler):

    CONSENSUS_ADDRESS = hash512(FAMILY_NAME)[:6] + '0' * 64

    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            ConsensusAccountMethod.SEND_REWARD: {
                PB_CLASS: EmptyPayload,
                PROCESSOR: self._send_reward,
                VALIDATOR: ProtoForm,
            },
        }

    def _send_reward(self, context, public_key, pb_payload):
        block = self.get_latest_block_info(context)

        signer_node_address = NodeAccountHandler().make_address_from_data(block.signer_public_key)
        node_account, consensus_account, zero_account = get_multiple_data(context, [
            (signer_node_address, NodeAccount),
            (self.CONSENSUS_ADDRESS, ConsensusAccount),
            (ZERO_ADDRESS, Account),
        ])

        if not node_account:
            raise InvalidTransaction('Node account not found.')

        if not consensus_account:
            raise InvalidTransaction('Consensus account not found.')

        if not zero_account:
            raise InvalidTransaction('Zero account not found.')

        genesis_node_address = AccountHandler().make_address_from_data(consensus_account.public_key)
        genesis_account = get_data(context, Account, genesis_node_address)

        if not genesis_account:
            raise InvalidTransaction('Genesis node account not found.')

        try:
            bet = consensus_account.bets.pop(signer_node_address)
        except KeyError:
            raise InvalidTransaction('Bet for address not found.')
        else:
            obligatory_payments = consensus_account.obligatory_payments

            # TODO: Take from here in the future
            # block_cost = consensus_account.block_cost
            block_cost = zero_account.balance


        min_stake, initial_stake, max_share, min_share = self._get_share_data(context)

        reputational = node_account.reputation.unfrozen + node_account.reputation.frozen

        reward = obligatory_payments + block_cost + bet

        state = {
            signer_node_address: node_account,
            self.CONSENSUS_ADDRESS: consensus_account,
            # TODO: Remove int he future
            ZERO_ADDRESS: zero_account,
        }

        if initial_stake <= reputational < min_stake * initial_stake:
            share = self._calculate_share(max_share, min_share, initial_stake,
                                          min_stake, reputational)
            calc = int(share * reward)
            node_account.reputation.unfrozen += calc
            node_account.reputation.frozen += int(reward - calc)
        elif reputational >= min_stake * initial_stake:
            calc = int(max_share * reward)
            node_account.reputation.unfrozen += calc
            genesis_account.balance += int(reward - calc)

            state[genesis_node_address] = genesis_account
        else:
            calc = int(max_share * reward)
            node_account.reputation.frozen += calc
            genesis_account.balance += int(reward - calc)

            state[genesis_node_address] = genesis_account

        consensus_account.obligatory_payments = 0

        # TODO: Use this for withdraw
        # consensus_account.block_cost = 0
        zero_account.balance = 0

        return state

    @staticmethod
    def _get_share_data(context):
        min_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)
        if min_stake is None or not min_stake.isdigit():
            raise InvalidTransaction(f'{SETTINGS_MINIMUM_STAKE} is malformed. Should be not negative integer.')
        min_stake = int(min_stake)

        initial_stake = _get_setting_value(context, SETTINGS_COMMITTEE_SIZE)
        if initial_stake is None or not initial_stake.isdigit():
            raise InvalidTransaction(f'{SETTINGS_COMMITTEE_SIZE} is malformed. Should be not negative integer.')
        initial_stake = int(initial_stake)

        ledger_tax = _get_setting_value(context, SETTINGS_BLOCKCHAIN_TAX)
        if ledger_tax is None:
            raise InvalidTransaction(f'{SETTINGS_BLOCKCHAIN_TAX} is malformed. Not set.')
        ledger_tax = float(ledger_tax)

        min_share = _get_setting_value(context, SETTINGS_MIN_SHARE)
        if min_share is None:
            raise InvalidTransaction(f'{SETTINGS_MIN_SHARE} is malformed. Not set.')
        min_share = float(min_share)

        max_share = 1 - ledger_tax

        return min_stake, initial_stake, max_share, min_share

    @staticmethod
    def _calculate_share(max_share, min_share, initial_stake, min_stake, reputational):
        return (
            ((max_share - min_share) / ((initial_stake - 1) * min_stake)) *
            (reputational - min_stake)
        ) + min_share