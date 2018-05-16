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
import hashlib
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_signing.secp256k1 import Secp256k1PublicKey, Secp256k1Context

from remme.protos.atomic_swap_pb2 import AtomicSwapMethod, AtomicSwapInitPayload, AtomicSwapInfo, \
    AtomicSwapApprovePayload, AtomicSwapExpirePayload, AtomicSwapSetSecretLockPayload, AtomicSwapClosePayload
from remme.protos.token_pb2 import TransferPayload
from remme.settings import SETTINGS_KEY_PUB_ENCRYPTION_KEY, SETTINGS_KEY_GENESIS_OWNERS, \
    SETTINGS_SWAP_COMMISSION, ZERO_ADDRESS
from remme.settings.helper import _make_settings_key, _get_setting_value
from remme.shared.basic_handler import BasicHandler, get_data
from remme.shared.utils import hash256
from remme.token_tp.client import TokenClient
from remme.token_tp.handler import TokenHandler, get_account_by_address
from remme.protos.certificate_pb2 import CertificateStorage, \
    NewCertificatePayload, RevokeCertificatePayload, CertificateMethod
from remme.shared.singleton import singleton

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'AtomicSwap'
FAMILY_VERSIONS = ['0.1']


RANGE_ACCEPTANCE = 1

# hours
INTIATOR_TIME_LOCK = 24
NON_INTIATOR_TIME_LOCK = 48

INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=INTIATOR_TIME_LOCK)
NON_INITIATOR_TIME_DELTA_LOCK = datetime.timedelta(hours=NON_INTIATOR_TIME_LOCK)


@singleton
class AtomicSwapHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            AtomicSwapMethod.INIT: {
                'pb_class': AtomicSwapInitPayload,
                'processor': self._swap_init
            },
            AtomicSwapMethod.APPROVE: {
                'pb_class': AtomicSwapApprovePayload,
                'processor': self._swap_approve
            },
            AtomicSwapMethod.EXPIRE: {
                'pb_class': AtomicSwapExpirePayload,
                'processor': self._swap_expire
            },
            AtomicSwapMethod.SET_SECRET_LOCK: {
                'pb_class': AtomicSwapSetSecretLockPayload,
                'processor': self._swap_set_lock
            },
            AtomicSwapMethod.CLOSE: {
                'pb_class': AtomicSwapClosePayload,
                'processor': self._swap_close
            },
        }

    def get_swap_info_from_swap_id(self, context, swap_id, to_raise_exception=True):
        swap_info = get_data(context, AtomicSwapInfo, self.make_address_from_data(swap_id))
        if to_raise_exception and not swap_info:
            raise InvalidTransaction('Atomic swap was not initiated for {} swap id!'.format(swap_id))
        return swap_info

    def get_state_update(self, swap_info):
        return {self.make_address_from_data(swap_info.swap_id): swap_info}

    def get_datetime_from_timestamp(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    def _swap_init(self, context, signer_pubkey, swap_init_payload):
        """
        if SecretLockOptionalBob is provided, Bob uses _swap_init to respond to requested swap
        Otherwise, Alice uses _swap_init to request a swap and thus, Bob can't receive funds until Alice "approves".
        """
        LOGGER.info("0. Check if swap ID already exists")
        LOGGER.info("0. swap payload {}".format(swap_init_payload))
        # 0. Check if swap ID already exists
        LOGGER.info("0. swap_id: {}".format(swap_init_payload.swap_id))
        if self.get_swap_info_from_swap_id(context, swap_init_payload.swap_id, to_raise_exception=False):
            raise InvalidTransaction('Atomic swap ID has already been taken, please use a different one!')
        # END

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = swap_init_payload.swap_id
        swap_info.is_closed = False
        swap_info.amount = swap_init_payload.amount
        swap_info.created_at = swap_init_payload.created_at
        swap_info.email_address_encrypted_optional = swap_init_payload.email_address_encrypted_optional_alice
        swap_info.sender_address = TokenHandler.make_address_from_data(signer_pubkey)
        swap_info.sender_address_non_local = swap_init_payload.sender_address_non_local
        swap_info.receiver_address = swap_init_payload.receiver_address

        if not TokenHandler.is_handler_address(swap_info.receiver_address):
            raise InvalidTransaction('Receiver address is not of a Token type.')

        LOGGER.info("1. Ensure transaction initiated within an hour")
        # 1. Ensure transaction initiated within an hour
        swap_info.secret_lock = swap_init_payload.secret_lock_optional_bob
        created_at = self.get_datetime_from_timestamp(swap_info.created_at)
        now = datetime.datetime.now()

        if not (now - datetime.timedelta(hours=1) < created_at < now):
            raise InvalidTransaction('Transaction is created a long time ago or timestamp is assigned set.')
        # END

        LOGGER.info("2. Check weather the sender is Alice")
        # 2. Check weather the sender is Alice:
        swap_info.is_initiator = not swap_init_payload.secret_lock_optional_bob
        # if Bob
        swap_info.is_approved = not swap_info.is_initiator
        # END

        # 3. Transfer funds to zero address.
        LOGGER.info("3. Transfer funds to zero address")
        commission = int(_get_setting_value(context, SETTINGS_SWAP_COMMISSION))
        if commission < 0:
            raise InvalidTransaction('Wrong commission address.')
        LOGGER.info("4. Get sender's account {}".format(swap_info.sender_address))
        account = get_account_by_address(context, swap_info.sender_address)
        total_amount = swap_info.amount + commission
        if account.balance < total_amount:
            raise InvalidTransaction('Not enough balance to perform the transaction in '
                                     'the amount (with a commission) {}.'.format(total_amount))

        transfer_payload = TokenClient.get_transfer_payload(ZERO_ADDRESS, total_amount)
        token_updated_state = TokenHandler._transfer_from_address(context,
                                                            swap_info.sender_address,
                                                            transfer_payload)
        LOGGER.info("Save state")

        return {**self.get_state_update(swap_info),  **token_updated_state}

    def _swap_approve(self, context, signer_pubkey, swap_approve_payload):
        """

        Only called by Alice to approve REMchain => other transaction for Bob to close it.

        """
        LOGGER.info('swap id: {}'.format(swap_approve_payload.swap_id))
        swap_info = self.get_swap_info_from_swap_id(context, swap_approve_payload.swap_id)

        if not swap_info.is_initiator and swap_info.receiver_address != TokenHandler.make_address_from_data(signer_pubkey):
            raise InvalidTransaction('Only transaction initiator (Alice) may approve the swap, '
                                     'once Bob provided a secret lock.')
        if not swap_info.secret_lock:
            raise InvalidTransaction('Secret Lock is needed for Bob to provide a secret key.')

        if swap_info.is_closed:
            raise InvalidTransaction('Swap id {} is already closed.'.format(swap_info.swap_id))

        swap_info.is_approved = True

        return self.get_state_update(swap_info)

    def _swap_expire(self, context, signer_pubkey, swap_expire_payload):
        """
        Transaction initiator (Alice) decides to withdraw deposit in 24 hours, or Bob in 48 hours

        """

        swap_info = self.get_swap_info_from_swap_id(context, swap_expire_payload.swap_id)

        if TokenHandler.make_address_from_data(signer_pubkey) != swap_info.sender_address:
            raise InvalidTransaction('Signer is not the one who opened the swap.')

        now = datetime.datetime.now()
        created_at = self.get_datetime_from_timestamp(swap_info.created_at)
        time_delta = INITIATOR_TIME_DELTA_LOCK if swap_info.is_initiator else NON_INITIATOR_TIME_DELTA_LOCK
        if (created_at + time_delta) > now:
            intiator_name = "initiator" if swap_info.is_initiator else "non initiator"
            raise InvalidTransaction('Swap {} needs to wait {} hours since timestamp: {} to withdraw.'.format(
                                        intiator_name, INTIATOR_TIME_LOCK, swap_info.created_at))

        swap_info.closed = True

        transfer_payload = TransferPayload()
        transfer_payload.address_to = swap_info.sender_address
        transfer_payload.amount = swap_info.amount
        token_updated_state = TokenHandler()._transfer_from_address(context,
                                                                    ZERO_ADDRESS,
                                                                    transfer_payload)

        return {**self.get_state_update(swap_info), **token_updated_state}

    def _swap_set_lock(self, context, signer_pubkey, swap_set_lock_payload):
        """
        Bob sets secret lock if Alice is initiator for REMchain => ETH transaction.
        Bob deposits escrow funds to zero address.
        Only works for Bob, Alice is the only one to approve

        """
        swap_info = self.get_swap_info_from_swap_id(context, swap_set_lock_payload.swap_id)

        if swap_info.secret_lock:
            raise InvalidTransaction('Secret lock is already added for {}.'.format(swap_info.swap_id))

        swap_info.secret_lock = swap_set_lock_payload.secret_lock

        return self.get_state_update(swap_info)

    def _swap_close(self, context, signer_pubkey, swap_close_payload):
        """
        Bob or Alice closes the swap by providing the secret key which matches secret lock.
        Requires "is_approved = True"
        Requires hash of secret key to match secret lock

        """
        swap_info = self.get_swap_info_from_swap_id(context, swap_close_payload.swap_id)

        if not swap_info.secret_lock:
            raise InvalidTransaction('Secret lock is required to close the swap!')

        if hash256(swap_close_payload.secret_key) != swap_info.secret_lock:
            raise InvalidTransaction('Secret key doesn\'t match specified secret lock!')

        if not swap_info.is_approved:
            raise InvalidTransaction('Transaction cannot be closed before it\'s approved.')

        transfer_payload = TokenClient.get_transfer_payload(swap_info.receiver_address, swap_info.amount)
        token_updated_state = TokenHandler._transfer_from_address(context,
                                                                    ZERO_ADDRESS,
                                                                    transfer_payload)

        swap_info.is_closed = True

        return {**self.get_state_update(swap_info), **token_updated_state}
