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

import json
import logging
from decimal import Decimal, getcontext, ROUND_UP
from datetime import datetime, timedelta
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.block_pb2 import BlockHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from google.protobuf.json_format import MessageToDict, ParseDict
# from sawtooth_validator.journal.batch_injector import BatchInjector
# from sawtooth_validator.protobuf.batch_pb2 import (
#     Batch,
#     BatchHeader,
#     BlockHeader,
# )

from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
    CloseMasternodePayload
)

from remme.protos.atomic_swap_pb2 import AtomicSwapMethod
from remme.protos.pub_key_pb2 import PubKeyMethod
from remme.protos.account_pb2 import AccountMethod
from remme.protos.obligatory_payment_pb2 import ObligatoryPaymentMethod

from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.clients.block_info import BlockInfoClient, CONFIG_ADDRESS


from remme.shared.forms import (
    NodeAccountInternalTransferPayloadForm,
    CloseMasternodePayloadForm
)

from remme.settings import (
    SETTINGS_MINIMUM_STAKE,
    SETTINGS_BLOCKCHAIN_TAX,
    SETTINGS_SWAP_COMMISSION,
    SETTINGS_OBLIGATORY_PAYMENT,
)
from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)
from remme.shared.utils import hash512, parse_header, isDigit
from remme.settings.helper import _get_setting_value
LOGGER = logging.getLogger(__name__)

MINIMUM_REWARD = 0.45
DEFROST_ACCELERATION = 10

PUB_KEY_STORE_PRICE = 10
PUB_KEY_MAX_VALIDITY = timedelta(365)

getcontext().prec = 20

FAMILY_NAME = 'node_account'
FAMILY_VERSIONS = ['0.1']


def get_block_cost(context, block):
    parse_header(BlockHeader, block)
    if 'batches' in block:
        block['batches_cost'] = [
            get_batch_cost(batch, context) for batch in block['batches']]

    return block['batches_cost']


def get_batch_cost(batch, context, batch_cost=0):
    swap_commission = int(_get_setting_value(context, SETTINGS_SWAP_COMMISSION))

    if swap_commission < 0:
        raise InvalidTransaction('Wrong commission address.')

    obligatory_payment = _get_setting_value(context, SETTINGS_OBLIGATORY_PAYMENT)

    if obligatory_payment is None or not isDigit(obligatory_payment):
        raise InvalidTransaction('Wrong obligatory payment address.')

    commissions = {
        'bet_node': 1000,
        'swap_commission': swap_commission,
        'pub_key_store': PUB_KEY_STORE_PRICE,
        'obligatory_payment': obligatory_payment
    }
    BetMethod = 'bet'

    parse_header(BatchHeader, batch)
    if 'transactions' in batch:
        for tx in batch['transactions']:
            tx_method = tx['payload'].method

            if tx_method is AtomicSwapMethod.INIT:
                batch_cost += commissions['swap_commission']
            elif tx_method is ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT:
                batch_cost += commissions['obligatory_payment']
            elif tx_method is BetMethod:
                batch_cost += commissions['bet_node']
            elif tx_method is PubKeyMethod.STORE_AND_PAY or PubKeyMethod.STORE:
                batch_cost += commissions['pub_key_store']

    return batch_cost


def get_latest_block(context):
    block_info_config = get_data(context, BlockInfoConfig, CONFIG_ADDRESS)

    if not block_info_config:
        raise InvalidTransaction('Block config not found.')

    latest_block = get_block_by_num(context=context, block_num=block_info_config.latest_block)
    return latest_block


def get_block_by_num(context, block_num):

    latest_block = get_data(
        context,
        BlockInfo,
        BlockInfoClient.create_block_address(block_num),
    )

    return latest_block


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
        }

    @staticmethod
    def get_omega_past(block_last_id, blocks, latest_block_timestamp, omega_past=0):
        block_nums = sorted(blocks.keys())
        block_nums = [num for num in block_nums if num >= int(block_last_id)]
        latest_block_timestamp = datetime.fromtimestamp(latest_block_timestamp)
        latest_id = None

        for block_id in block_nums:
            block_time = datetime.fromtimestamp(int(blocks[block_id]['timestamp']))
            if latest_block_timestamp - block_time < PUB_KEY_MAX_VALIDITY:
                latest_id = block_id
                break

            omega_past += blocks[block_id]['omega']

        return omega_past, latest_id

    @staticmethod
    def get_dict_node_account_blocks(context, node_account_public_key):
        block_info_config = get_data(context, BlockInfoConfig, CONFIG_ADDRESS)
        node_account_blocks = {}

        if not block_info_config:
            raise InvalidTransaction('Block config not found.')

        for current_block in range(block_info_config.latest_block, block_info_config.oldest_block, -1):
            current_block_addr = BlockInfoClient.create_block_address(current_block)
            current_block_info = get_data(context, BlockInfo, current_block_addr)

            if current_block_info.signer_public_key == node_account_public_key:
                node_account_blocks[current_block_info.block_num] = \
                    MessageToDict(message=current_block_info, preserving_proto_field_name=True)

        if node_account_blocks:
            latest_block = node_account_blocks[max(node_account_blocks.keys())]
            return node_account_blocks, latest_block

        return node_account_blocks, None

    def _get_available_pct_distribution_reward(self, context, node_account_public_key):
        node_account_address = self.make_address_from_data(node_account_public_key)
        node_account = get_data(context, NodeAccount, node_account_address)
        minimum_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)
        blockchain_tax = _get_setting_value(context, SETTINGS_BLOCKCHAIN_TAX)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if minimum_stake is None or not minimum_stake.isdigit():
            raise InvalidTransaction('Wrong minimum stake address.')

        if blockchain_tax is None or not isDigit(blockchain_tax):
            raise InvalidTransaction('Wrong blockchain tax address.')

        minimum_stake = int(minimum_stake)
        max_reward = 1 - float(blockchain_tax)

        if node_account.reputation.frozen < minimum_stake:
            raise InvalidTransaction('Frozen balance is lower than the minimum stake.')

        if node_account.reputation.frozen >= DEFROST_ACCELERATION * minimum_stake:
            return Decimal(str(max_reward))

        reward_span = Decimal(str(max_reward - MINIMUM_REWARD)) / Decimal(str(DEFROST_ACCELERATION - 1))
        quantity_stakes = Decimal(str(node_account.reputation.frozen - minimum_stake)) / Decimal(str(minimum_stake))

        available_pct_distribution_reward = reward_span * quantity_stakes + Decimal(str(MINIMUM_REWARD))

        return available_pct_distribution_reward

    def _get_available_amount_defrosting_tokens_to_unfrozen(self, context, node_account_public_key):
        current_block = get_latest_block(context)  # DEBUG VERSION

        node_account_address = self.make_address_from_data(node_account_public_key)
        node_account = get_data(context, NodeAccount, node_account_address)
        minimum_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)
        blockchain_tax = _get_setting_value(context, SETTINGS_BLOCKCHAIN_TAX)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if minimum_stake is None or not minimum_stake.isdigit():
            raise InvalidTransaction('Wrong minimum stake address.')

        if blockchain_tax is None or not isDigit(blockchain_tax):
            raise InvalidTransaction('Wrong blockchain tax address.')

        minimum_stake = int(minimum_stake)
        if node_account.reputation.frozen < minimum_stake:
            raise InvalidTransaction('Frozen balance is lower than the minimum stake.')

        max_reward = Decimal(str(1 - float(blockchain_tax)))
        # current_block_cost = str(sum(get_block_cost(context, current_block)))
        current_block_cost = Decimal(current_block.block_cost)  # DEBUG VERSION
        current_block_time = datetime.fromtimestamp(current_block.timestamp)

        pct_distribution_reward = self._get_available_pct_distribution_reward(context, node_account_public_key)
        node_account_blocks, latest_node_block = self.get_dict_node_account_blocks(context, node_account_public_key)

        frozen_reward = (max_reward - pct_distribution_reward) * current_block_cost
        omega_past = 0

        if latest_node_block:
            omega = Decimal(str(latest_node_block['omega'])) + frozen_reward
            block_oldest_id = int(latest_node_block['node_oldest_block_id'])
            oldest_block = get_block_by_num(context, block_oldest_id)
            oldest_block_time = datetime.fromtimestamp(oldest_block.timestamp)
            latest_node_block_time = datetime.fromtimestamp(int(latest_node_block['timestamp']))

            if current_block_time - oldest_block_time > PUB_KEY_MAX_VALIDITY:
                omega_past, block_oldest_id = self.get_omega_past(
                    block_last_id=block_oldest_id,
                    blocks=node_account_blocks,
                    latest_block_timestamp=current_block.timestamp,
                )
                omega_past = Decimal(str(omega_past))
        else:
            omega = frozen_reward
            latest_node_block_time = current_block_time
            block_oldest_id = current_block.block_num

        instant_reward = pct_distribution_reward * current_block_cost

        time_block_delta = current_block_time - latest_node_block_time
        omega_delta = str(omega - omega_past)

        reward = instant_reward + Decimal(omega_delta) * Decimal(time_block_delta/PUB_KEY_MAX_VALIDITY)
        reward = int(reward.quantize(Decimal('1.'), rounding=ROUND_UP))

        return reward, block_oldest_id

    def _initialize_masternode(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            node_account = NodeAccount()

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

        return {
            node_account_address: node_account,
        }

    def _close_masternode(self, context, node_account_public_key, payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.node_state != NodeAccount.OPENED:
            raise InvalidTransaction('Masternode is not opened or has been closed.')

        node_account.node_state = NodeAccount.CLOSED

        node_account.balance += node_account.reputation.frozen
        node_account.balance += node_account.reputation.unfrozen

        node_account.reputation.frozen = 0
        node_account.reputation.unfrozen = 0

        return {
            node_account_address: node_account,
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

        minimum_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)

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
