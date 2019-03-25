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


from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeState,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
    CloseMasternodePayload,
    SetBetPayload,
)

from remme.shared.forms import (
    NodeAccountInternalTransferPayloadForm,
    CloseMasternodePayloadForm,
    NodeAccountGenesisForm,
    SetBetPayloadForm,
)

from remme.settings import (
    SETTINGS_MINIMUM_STAKE, SETTINGS_GENESIS_OWNERS, NODE_STATE_ADDRESS)

from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)
from remme.settings.helper import _get_setting_value


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'node_account'
FAMILY_VERSIONS = ['0.1']


class NodeAccountHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._transfer_from_unfrozen_to_operational,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.GENESIS_NODE: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._initialize_node,
                VALIDATOR: NodeAccountGenesisForm,
            },
            NodeAccountMethod.INITIALIZE_MASTERNODE: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._initialize_masternode,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.CLOSE_MASTERNODE: {
                PROCESSOR: self._close_masternode,
                PB_CLASS: CloseMasternodePayload,
                VALIDATOR: CloseMasternodePayloadForm,
            },
            NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._transfer_from_frozen_to_unfrozen,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.SET_BET: {
                PB_CLASS: SetBetPayload,
                PROCESSOR: self._set_bet,
                VALIDATOR: SetBetPayloadForm,
            },
        }

    def _initialize_node(self, context, node_account_public_key, internal_transfer_payload):
        genesis_owners = _get_setting_value(context, SETTINGS_GENESIS_OWNERS)
        genesis_owners = genesis_owners.split(',') \
            if genesis_owners is not None else []

        if node_account_public_key not in genesis_owners:
            raise InvalidTransaction(
                'Node account could be created only by current node.')

        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            node_account = NodeAccount(
                balance=internal_transfer_payload.value
            )
        else:
            raise InvalidTransaction('Node account already exists.')

        LOGGER.info(f"Node account \"{node_account_address}\" created")

        return {
            node_account_address: node_account,
        }

    def _initialize_masternode(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account, node_state = get_multiple_data(context, [
            (node_account_address, NodeAccount),
            (NODE_STATE_ADDRESS, NodeState),
        ])

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.node_state != NodeAccount.NEW:
            raise InvalidTransaction('Masternode is already opened or closed.')

        if node_account.balance < internal_transfer_payload.value:
            raise InvalidTransaction('Insufficient amount of tokens on operational account.')

        minimum_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)
        if minimum_stake is None or not minimum_stake.isdigit():
            raise InvalidTransaction('remme.settings.minimum_stake is malformed. Should be not negative integer.')
        minimum_stake = int(minimum_stake)

        if internal_transfer_payload.value < minimum_stake:
            raise InvalidTransaction('Initial stake is too low.')

        node_account.node_state = NodeAccount.OPENED

        node_account.balance -= internal_transfer_payload.value

        unfrozen_part = internal_transfer_payload.value - minimum_stake
        node_account.reputation.frozen += minimum_stake
        node_account.reputation.unfrozen += unfrozen_part

        if node_state is None:
            node_state = NodeState()

        if node_account_address not in node_state.master_nodes:
            node_state.master_nodes.append(node_account_address)

        return {
            node_account_address: node_account,
            NODE_STATE_ADDRESS: node_state,
        }

    def _close_masternode(self, context, node_account_public_key, payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account, node_state = get_multiple_data(context, [
            (node_account_address, NodeAccount),
            (NODE_STATE_ADDRESS, NodeState),
        ])

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.node_state != NodeAccount.OPENED:
            raise InvalidTransaction('Masternode is not opened or has been closed.')

        node_account.node_state = NodeAccount.CLOSED

        node_account.balance += node_account.reputation.frozen
        node_account.balance += node_account.reputation.unfrozen

        node_account.reputation.frozen = 0
        node_account.reputation.unfrozen = 0

        if node_state is None:
            node_state = NodeState()

        if node_account_address in node_state.master_nodes:
            node_state.master_nodes.remove(node_account_address)

        return {
            node_account_address: node_account,
            NODE_STATE_ADDRESS: node_state,
        }

    def _transfer_from_unfrozen_to_operational(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.reputation.unfrozen < internal_transfer_payload.value:
            raise InvalidTransaction('Insufficient amount of tokens on unfrozen account.')

        node_account.reputation.unfrozen -= internal_transfer_payload.value
        node_account.balance += internal_transfer_payload.value

        return {
            node_account_address: node_account,
        }

    def _transfer_from_frozen_to_unfrozen(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)
        minimum_stake = _get_setting_value(context, 'remme.settings.minimum_stake')

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if minimum_stake is None or not minimum_stake.isdigit():
            raise InvalidTransaction('Wrong minimum stake address.')

        minimum_stake = int(minimum_stake)

        if node_account.reputation.frozen < minimum_stake:
            raise InvalidTransaction('Frozen balance is lower than the minimum stake.')

        if node_account.reputation.frozen - internal_transfer_payload.value < minimum_stake:
            raise InvalidTransaction('Frozen balance after transfer lower than the minimum stake.')

        node_account.reputation.frozen -= internal_transfer_payload.value
        node_account.reputation.unfrozen += internal_transfer_payload.value

        return {
            node_account_address: node_account,
        }

    def _set_bet(self, context, node_account_public_key, pb_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        bet_name = pb_payload.WhichOneof('bet')
        bet_payload = getattr(pb_payload, str(bet_name))

        try:
            setattr(node_account, bet_name, bet_payload)
        except AttributeError as e:
            LOGGER.exception(e)
            raise InvalidTransaction('Failed to update bet config.')

        return {
            node_account_address: node_account,
        }
