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

import datetime
import logging
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.account_pb2 import Account
from remme.protos.atomic_swap_pb2 import (
    AtomicSwapMethod, AtomicSwapInitPayload, AtomicSwapInfo,
    AtomicSwapApprovePayload, AtomicSwapExpirePayload,
    AtomicSwapSetSecretLockPayload, AtomicSwapClosePayload
)
from remme.settings import SETTINGS_SWAP_COMMISSION, ZERO_ADDRESS
from remme.settings.helper import _get_setting_value

from remme.tp.basic import (
    BasicHandler,
    get_data,
    PROCESSOR,
    PB_CLASS,
)
from remme.shared.utils import web3_hash

from remme.clients.account import AccountClient
from remme.clients.block_info import BlockInfoClient, CONFIG_ADDRESS
from remme.tp.account import AccountHandler, get_account_by_address
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig

from remme.shared.constants import Events, EMIT_EVENT


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'AtomicSwap'
FAMILY_VERSIONS = ['0.1']


RANGE_ACCEPTANCE = 1

# hours
INTIATOR_TIME_LOCK = 24
NON_INTIATOR_TIME_LOCK = 48

INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=INTIATOR_TIME_LOCK)
NON_INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=NON_INTIATOR_TIME_LOCK)

NOT_PERMITTED_TO_CHANGE_SWAP_STATUSES = (AtomicSwapInfo.CLOSED, AtomicSwapInfo.EXPIRED)


class AtomicSwapHandler(BasicHandler):
    """
    Atomic swap implementation.

    References:
        - https://github.com/decred/atomicswap
    """
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            AtomicSwapMethod.INIT: {
                PB_CLASS: AtomicSwapInitPayload,
                PROCESSOR: self._swap_init,
                EMIT_EVENT: Events.SWAP_INIT.value
            },
            AtomicSwapMethod.APPROVE: {
                PB_CLASS: AtomicSwapApprovePayload,
                PROCESSOR: self._swap_approve,
                EMIT_EVENT: Events.SWAP_APPROVE.value
            },
            AtomicSwapMethod.EXPIRE: {
                PB_CLASS: AtomicSwapExpirePayload,
                PROCESSOR: self._swap_expire,
                EMIT_EVENT: Events.SWAP_EXPIRE.value
            },
            AtomicSwapMethod.SET_SECRET_LOCK: {
                PB_CLASS: AtomicSwapSetSecretLockPayload,
                PROCESSOR: self._swap_set_lock,
                EMIT_EVENT: Events.SWAP_SET_SECRET_LOCK.value
            },
            AtomicSwapMethod.CLOSE: {
                PB_CLASS: AtomicSwapClosePayload,
                PROCESSOR: self._swap_close,
                EMIT_EVENT: Events.SWAP_CLOSE.value
            },
        }

    @staticmethod
    def get_datetime_from_timestamp(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def _get_latest_block_info(context):
        block_info_config = get_data(context, BlockInfoConfig, CONFIG_ADDRESS)

        if not block_info_config:
            raise InvalidTransaction('Block config not found.')

        LOGGER.info(f'Current latest block number: {block_info_config.latest_block + 1}')

        block_info = get_data(context, BlockInfo, BlockInfoClient.create_block_address(block_info_config.latest_block))

        if not block_info:
            raise InvalidTransaction(f'Block {block_info_config.latest_block + 1} not found.')

        LOGGER.info(f'Block with number successfully loaded: {block_info.block_num + 1}')

        return block_info

    def _swap_init(self, context, signer_pubkey, swap_init_payload):
        """
        if SecretLockOptionalBob is provided, Bob uses _swap_init to respond to requested swap
        Otherwise, Alice uses _swap_init to request a swap and thus, Bob can't receive funds until Alice "approves".
        """
        address_swap_info_is_stored_by = self.make_address_from_data(swap_init_payload.swap_id)
        swap_information = get_data(context, AtomicSwapInfo, address_swap_info_is_stored_by)

        if swap_information:
            raise InvalidTransaction('Atomic swap ID has already been taken, please use a different one.')

        block_info = self._get_latest_block_info(context)
        block_time = block_info.timestamp

        swap_information = AtomicSwapInfo()
        swap_information.swap_id = swap_init_payload.swap_id
        swap_information.state = AtomicSwapInfo.OPENED
        swap_information.amount = swap_init_payload.amount
        swap_information.created_at = block_time
        swap_information.secret_lock = swap_init_payload.secret_lock_by_solicitor
        swap_information.email_address_encrypted_optional = swap_init_payload.email_address_encrypted_by_initiator
        swap_information.sender_address = AccountHandler().make_address_from_data(signer_pubkey)
        swap_information.sender_address_non_local = swap_init_payload.sender_address_non_local
        swap_information.receiver_address = swap_init_payload.receiver_address
        swap_information.is_initiator = not swap_init_payload.secret_lock_by_solicitor

        if not AccountHandler().is_handler_address(swap_information.receiver_address):
            raise InvalidTransaction('Receiver address is not of a blockchain token type.')

        commission_amount = int(_get_setting_value(context, SETTINGS_SWAP_COMMISSION))
        if commission_amount < 0:
            raise InvalidTransaction('Wrong commission address.')

        swap_total_amount = swap_information.amount + commission_amount

        account = get_data(context, Account, swap_information.sender_address)

        if account is None:
            account = Account()

        if account.balance < swap_total_amount:
            raise InvalidTransaction(
                f'Not enough balance to perform the transaction in the amount (with a commission) {swap_total_amount}.'
            )

        transfer_payload = AccountClient.get_transfer_payload(ZERO_ADDRESS, commission_amount)

        transfer_state = AccountHandler()._transfer_from_address(
            context, swap_information.sender_address, transfer_payload,
        )

        sender_account = transfer_state.get(swap_information.sender_address)
        sender_account.balance -= swap_information.amount

        return {
            address_swap_info_is_stored_by: swap_information,
            **transfer_state,
        }

    def _swap_set_lock(self, context, signer_pubkey, swap_set_lock_payload):
        """
        Set secret lock.

        Bob sets secret lock if Alice is initiator for REMchain => ETH transaction.
        Bob deposits escrow funds to zero address.
        Only works for Bob, Alice is the only one to approve
        """
        swap_identifier = swap_set_lock_payload.swap_id

        address_swap_info_is_stored_by = self.make_address_from_data(swap_identifier)
        swap_information = get_data(context, AtomicSwapInfo, address_swap_info_is_stored_by)

        if not swap_information:
            raise InvalidTransaction(f'Atomic swap was not initiated for identifier {swap_identifier}!')

        if swap_information.state in NOT_PERMITTED_TO_CHANGE_SWAP_STATUSES:
            raise InvalidTransaction(
                f'No operations can be done upon the swap: {swap_identifier} as it is already closed or expired.',
            )

        if swap_information.secret_lock:
            raise InvalidTransaction(f'Secret lock is already added for {swap_information.swap_id}.')

        swap_information.secret_lock = swap_set_lock_payload.secret_lock
        swap_information.state = AtomicSwapInfo.SECRET_LOCK_PROVIDED

        return {
            address_swap_info_is_stored_by: swap_information,
        }

    def _swap_approve(self, context, signer_pubkey, swap_approve_payload):
        """
        Only called by Alice to approve REMchain => other transaction for Bob to close it.
        """
        LOGGER.info(f'Approving atomic swap with identifier {swap_approve_payload.swap_id}.')

        signer_address = AccountHandler().make_address_from_data(signer_pubkey)
        swap_identifier = swap_approve_payload.swap_id

        address_swap_info_is_stored_by = self.make_address_from_data(swap_identifier)
        swap_information = get_data(context, AtomicSwapInfo, address_swap_info_is_stored_by)

        if not swap_information:
            raise InvalidTransaction(f'Atomic swap was not initiated for identifier {swap_identifier}!')

        if swap_information.state in NOT_PERMITTED_TO_CHANGE_SWAP_STATUSES:
            raise InvalidTransaction(
                f'No operations can be done upon the swap: {swap_identifier} as it is already closed or expired.',
            )

        if not swap_information.is_initiator or swap_information.sender_address != signer_address:
            raise InvalidTransaction(
                'Only transaction initiator (Alice) may approve the swap, once Bob provided a secret lock.',
            )

        if not swap_information.secret_lock:
            raise InvalidTransaction('Secret lock is needed for Bob to provide a secret key.')

        if swap_information.state != AtomicSwapInfo.SECRET_LOCK_PROVIDED:
            raise InvalidTransaction(f'Swap identifier {swap_information.swap_id} is already closed.')

        swap_information.state = AtomicSwapInfo.APPROVED

        return {
            address_swap_info_is_stored_by: swap_information,
        }

    def _swap_expire(self, context, signer_pubkey, swap_expire_payload):
        """
        Transaction initiator (Alice) decides to withdraw deposit in 24 hours, or Bob in 48 hours.
        """
        swap_identifier = swap_expire_payload.swap_id

        address_swap_info_is_stored_by = self.make_address_from_data(swap_identifier)
        swap_information = get_data(context, AtomicSwapInfo, address_swap_info_is_stored_by)

        if not swap_information:
            raise InvalidTransaction(f'Atomic swap was not initiated for identifier {swap_identifier}!')

        if swap_information.state in NOT_PERMITTED_TO_CHANGE_SWAP_STATUSES:
            raise InvalidTransaction(
                f'No operations can be done upon the swap: {swap_identifier} as it is already closed or expired.',
            )

        signer_address = AccountHandler().make_address_from_data(signer_pubkey)

        if signer_address != swap_information.sender_address:
            raise InvalidTransaction('Signer is not the one who opened the swap.')

        block = self._get_latest_block_info(context)
        block_time = self.get_datetime_from_timestamp(block.timestamp)
        created_at = self.get_datetime_from_timestamp(swap_information.created_at)

        time_delta = INITIATOR_TIME_DELTA_LOCK if swap_information.is_initiator else NON_INITIATOR_TIME_DELTA_LOCK

        if (created_at + time_delta) > block_time:
            initiator_name = 'initiator' if swap_information.is_initiator else 'non initiator'
            initiator_time_lock = INTIATOR_TIME_LOCK if swap_information.is_initiator else NON_INTIATOR_TIME_LOCK

            raise InvalidTransaction(
                f'Swap {initiator_name} needs to wait {initiator_time_lock} hours since '
                f'timestamp {swap_information.created_at} to withdraw.'
            )

        account = get_data(context, Account, swap_information.sender_address)
        if account is None:
            account = Account()
        account.balance += swap_information.amount

        swap_information.state = AtomicSwapInfo.EXPIRED

        return {
            address_swap_info_is_stored_by: swap_information,
            swap_information.sender_address: account,
        }

    def _swap_close(self, context, signer_pubkey, swap_close_payload):
        """
        Close atomic swap.

        Any party (Bob or Alice) can close atomic swap by providing secret key. If hash from secret key matches
        secret lock, secret key is valid. Closing atomic swap means participant (not initiator)
        get REMchain tokens instead ERC20 tokens.

        Closing requires atomic swap to be approved.
        """
        swap_identifier = swap_close_payload.swap_id

        address_swap_info_is_stored_by = self.make_address_from_data(swap_identifier)
        swap_information = get_data(context, AtomicSwapInfo, address_swap_info_is_stored_by)

        if not swap_information:
            raise InvalidTransaction(f'Atomic swap was not initiated for identifier {swap_identifier}!')

        if swap_information.state in NOT_PERMITTED_TO_CHANGE_SWAP_STATUSES:
            raise InvalidTransaction(
                f'No operations can be done upon the swap: {swap_identifier} as it is already closed or expired.',
            )

        if not swap_information.secret_lock:
            raise InvalidTransaction('Secret lock is required to close the swap.')

        if web3_hash(swap_close_payload.secret_key) != swap_information.secret_lock:
            raise InvalidTransaction('Secret key doesn\'t match specified secret lock.')

        if swap_information.is_initiator and swap_information.state != AtomicSwapInfo.APPROVED:
            raise InvalidTransaction('Transaction cannot be closed before it\'s approved.')

        account = get_data(context, Account, swap_information.receiver_address)
        if account is None:
            account = Account()
        account.balance += swap_information.amount

        swap_information.secret_key = swap_close_payload.secret_key
        swap_information.state = AtomicSwapInfo.CLOSED

        return {
            address_swap_info_is_stored_by: swap_information,
            swap_information.receiver_address: account,
        }
