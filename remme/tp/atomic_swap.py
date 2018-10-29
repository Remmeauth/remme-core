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

from remme.ws.basic import EMIT_EVENT
from remme.ws.constants import Events


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'AtomicSwap'
FAMILY_VERSIONS = ['0.1']


RANGE_ACCEPTANCE = 1

# hours
INTIATOR_TIME_LOCK = 24
NON_INTIATOR_TIME_LOCK = 48

INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=INTIATOR_TIME_LOCK)
NON_INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=NON_INTIATOR_TIME_LOCK)


class AtomicSwapHandler(BasicHandler):
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

    def get_swap_info_from_swap_id(self, context, swap_id, to_raise_exception=True):
        swap_info = get_data(context, AtomicSwapInfo,
                             self.make_address_from_data(swap_id))
        if to_raise_exception and not swap_info:
            raise InvalidTransaction(f'Atomic swap was not initiated '
                                     f'for {swap_id} swap id!')

        if swap_info and swap_info.state in [
            AtomicSwapInfo.CLOSED, AtomicSwapInfo.EXPIRED
        ]:
            raise InvalidTransaction('No operations can be done upon '
                                     f'the swap: {swap_id} '
                                     ' as it is already closed.')
        return swap_info

    def get_state_update(self, swap_info):
        return {self.make_address_from_data(swap_info.swap_id): swap_info}

    @staticmethod
    def get_datetime_from_timestamp(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    def _get_latest_block_info(self, context):
        bc = get_data(context, BlockInfoConfig, CONFIG_ADDRESS)
        if not bc:
            raise InvalidTransaction('Block config not found')

        LOGGER.info(f'Current latest block number: {bc.latest_block + 1}')

        block = get_data(context, BlockInfo,
                         BlockInfoClient.create_block_address(bc.latest_block))
        if not block:
            raise InvalidTransaction(f'Block "{bc.latest_block + 1}" '
                                     f'not found')

        LOGGER.info(f'Block with number successfully loaded: '
                    f'{block.block_num + 1}')

        return block

    def _swap_init(self, context, signer_pubkey, swap_init_payload):
        """
        if SecretLockOptionalBob is provided, Bob uses _swap_init to respond to requested swap
        Otherwise, Alice uses _swap_init to request a swap and thus, Bob can't receive funds until Alice "approves".
        """
        LOGGER.info("0. Check if swap ID already exists")
        # 0. Check if swap ID already exists
        if self.get_swap_info_from_swap_id(context, swap_init_payload.swap_id,
                                           to_raise_exception=False):
            raise InvalidTransaction('Atomic swap ID has already been taken, '
                                     'please use a different one!')
        # END

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = swap_init_payload.swap_id
        swap_info.state = AtomicSwapInfo.OPENED
        swap_info.amount = swap_init_payload.amount
        swap_info.created_at = swap_init_payload.created_at
        swap_info.email_address_encrypted_optional = \
            swap_init_payload.email_address_encrypted_by_initiator
        swap_info.sender_address = AccountHandler() \
            .make_address_from_data(signer_pubkey)
        swap_info.sender_address_non_local = \
            swap_init_payload.sender_address_non_local
        swap_info.receiver_address = swap_init_payload.receiver_address

        if not AccountHandler().is_handler_address(swap_info.receiver_address):
            raise InvalidTransaction('Receiver address is not of a Token type.')

        LOGGER.info("1. Ensure transaction initiated within an hour")
        # 1. Ensure transaction initiated within an hour
        swap_info.secret_lock = swap_init_payload.secret_lock_by_solicitor
        created_at = self.get_datetime_from_timestamp(swap_info.created_at)

        block = self._get_latest_block_info(context)
        block_time = self.get_datetime_from_timestamp(block.timestamp)

        if not (block_time - datetime.timedelta(hours=1) < created_at <= block_time):
            raise InvalidTransaction('Transaction is created a long time ago '
                                     'or timestamp is assigned set.')
        # END

        LOGGER.info("2. Check weather the sender is Alice")
        # 2. Check weather the sender is Alice:
        swap_info.is_initiator = not swap_init_payload.secret_lock_by_solicitor
        # END

        # 3. Transfer funds to zero address.
        LOGGER.info("3. Transfer funds to zero address")
        commission = int(_get_setting_value(context, SETTINGS_SWAP_COMMISSION))
        if commission < 0:
            raise InvalidTransaction('Wrong commission address.')
        LOGGER.info(f"4. Get sender's account {swap_info.sender_address}")
        account = get_account_by_address(context, swap_info.sender_address)
        total_amount = swap_info.amount + commission
        if account.balance < total_amount:
            raise InvalidTransaction(f'Not enough balance to perform '
                                     f'the transaction in '
                                     f'the amount (with a commission) '
                                     f'{total_amount}.')

        transfer_payload = AccountClient \
            .get_transfer_payload(ZERO_ADDRESS, total_amount)
        token_updated_state = AccountHandler() \
            ._transfer_from_address(context, swap_info.sender_address,
                                    transfer_payload)
        LOGGER.info("Save state")

        return {**self.get_state_update(swap_info), **token_updated_state}

    def _swap_approve(self, context, signer_pubkey, swap_approve_payload):
        """

        Only called by Alice to approve REMchain => other transaction for Bob to close it.

        """
        LOGGER.info('swap id: {}'.format(swap_approve_payload.swap_id))
        swap_info = self.get_swap_info_from_swap_id(context, swap_approve_payload.swap_id)

        if not swap_info.is_initiator or \
           swap_info.sender_address != AccountHandler() \
           .make_address_from_data(signer_pubkey):
            raise InvalidTransaction('Only transaction initiator (Alice) '
                                     'may approve the swap, '
                                     'once Bob provided a secret lock.')
        if not swap_info.secret_lock:
            raise InvalidTransaction('Secret Lock is needed for Bob '
                                     'to provide a secret key.')

        if swap_info.state != AtomicSwapInfo.SECRET_LOCK_PROVIDED:
            raise InvalidTransaction(f'Swap id {swap_info.swap_id} '
                                     'is already closed.')

        swap_info.state = AtomicSwapInfo.APPROVED

        return self.get_state_update(swap_info)

    def _swap_expire(self, context, signer_pubkey, swap_expire_payload):
        """
        Transaction initiator (Alice) decides to withdraw deposit in 24 hours, or Bob in 48 hours

        """

        swap_info = self.get_swap_info_from_swap_id(context, swap_expire_payload.swap_id)

        if AccountHandler() \
           .make_address_from_data(signer_pubkey) != swap_info.sender_address:
            raise InvalidTransaction('Signer is not the one who opened '
                                     'the swap.')

        block = self._get_latest_block_info(context)
        block_time = self.get_datetime_from_timestamp(block.timestamp)

        created_at = self.get_datetime_from_timestamp(swap_info.created_at)
        time_delta = INITIATOR_TIME_DELTA_LOCK \
            if swap_info.is_initiator else NON_INITIATOR_TIME_DELTA_LOCK
        if (created_at + time_delta) > block_time:
            intiator_name = "initiator" \
                if swap_info.is_initiator else "non initiator"
            raise InvalidTransaction(f'Swap {intiator_name} needs to wait '
                                     f'{INTIATOR_TIME_LOCK} hours since '
                                     f'timestamp: {swap_info.created_at} '
                                     f'to withdraw.')

        swap_info.state = AtomicSwapInfo.EXPIRED

        transfer_payload = AccountClient \
            .get_transfer_payload(swap_info.sender_address, swap_info.amount)
        token_updated_state = AccountHandler() \
            ._transfer_from_address(context, ZERO_ADDRESS, transfer_payload)

        return {**self.get_state_update(swap_info), **token_updated_state}

    def _swap_set_lock(self, context, signer_pubkey, swap_set_lock_payload):
        """
        Bob sets secret lock if Alice is initiator for REMchain => ETH transaction.
        Bob deposits escrow funds to zero address.
        Only works for Bob, Alice is the only one to approve

        """
        swap_info = self.get_swap_info_from_swap_id(context, swap_set_lock_payload.swap_id)

        if swap_info.secret_lock:
            raise InvalidTransaction(f'Secret lock is already added '
                                     f'for {swap_info.swap_id}.')

        swap_info.secret_lock = swap_set_lock_payload.secret_lock
        swap_info.state = AtomicSwapInfo.SECRET_LOCK_PROVIDED

        return self.get_state_update(swap_info)

    def _swap_close(self, context, signer_pubkey, swap_close_payload):
        """
        Bob or Alice closes the swap by providing the secret key which matches secret lock.
        Requires "is_approved = True"
        Requires hash of secret key to match secret lock

        """
        swap_info = self.get_swap_info_from_swap_id(context, swap_close_payload.swap_id)

        if not swap_info.secret_lock:
            raise InvalidTransaction('Secret lock is required to close '
                                     'the swap!')

        if web3_hash(swap_close_payload.secret_key) != swap_info.secret_lock:
            raise InvalidTransaction('Secret key doesn\'t match specified '
                                     'secret lock!')

        if swap_info.is_initiator and swap_info.state != AtomicSwapInfo.APPROVED:
            raise InvalidTransaction('Transaction cannot be closed '
                                     'before it\'s approved.')

        transfer_payload = AccountClient \
            .get_transfer_payload(swap_info.receiver_address, swap_info.amount)
        token_updated_state = AccountHandler() \
            ._transfer_from_address(context, ZERO_ADDRESS, transfer_payload)
        swap_info.secret_key = swap_close_payload.secret_key

        swap_info.state = AtomicSwapInfo.CLOSED

        return {**self.get_state_update(swap_info), **token_updated_state}
