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

from remme.protos.atomic_swap_pb2 import AtomicSwapMethod, AtomicSwapInitPayload, AtomicSwapInfo
from remme.protos.token_pb2 import TransferPayload
from remme.settings import SETTINGS_KEY_PUB_ENCRYPTION_KEY, SETTINGS_KEY_ALLOWED_GENESIS_MEMBERS
from remme.settings_tp.handler import _make_settings_key, _get_setting_value
from remme.shared.basic_handler import BasicHandler, get_data
from remme.token_tp.handler import TokenHandler
from remme.protos.certificate_pb2 import CertificateStorage, \
    NewCertificatePayload, RevokeCertificatePayload, CertificateMethod
from remme.shared.singleton import singleton

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'AtomicSwap'
FAMILY_VERSIONS = ['0.1']


RANGE_ACCEPTANCE = 1

@singleton
class AtomicSwapHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            AtomicSwapMethod.INIT: {
                'pb_class': AtomicSwapInitPayload,
                'processor': self._swap_init
            }
        }

    def _swap_init(self, context, signer_pubkey, swap_init_payload):
        """
        if SecretLockOptionalBob is provided, Bob uses _swap_init to respond to requested swap
        Otherwise, Alice uses _swap_init to request a swap and thus, Bob can't receive funds until Alice "approves".

        1. Verify if Alice or Bob is requesting(using settings_tp matching)
        2. if Bob: add funds from genesis and lock for 48 hours
        message AtomicSwapInitPayload {
            string receiverAddress = 1;
            string senderAddressNonLocal = 7;
            uint64 amount = 2;
            string swapID = 3;
            string secretLockOptionalBob = 4;
            string emailAddressEncryptedOptionalAlice = 5;
        }

        message AtomicSwapInfo {
            bool isClosed = 1;
            bool isApproved = 11;
            string senderAddress = 2;
            string receiverAddress = 3;
            uint64 amount = 4;
            string emailAddressEncryptedOptional = 5;
            string swapID = 6;
            string secretLock = 7;
            string secretKey = 8;
            uint32 created_at = 9;
            bool isInitiator = 10; // isAlice
        }
        """
        # TODO validate payloads
        atomic_swap_info = AtomicSwapInfo()

        atomic_swap_info.swapID = swap_init_payload.swapID
        atomic_swap_info.isClosed = False
        atomic_swap_info.isApproved = False
        atomic_swap_info.amount = swap_init_payload.amount
        atomic_swap_info.created_at = swap_init_payload.created_at
        atomic_swap_info.emailAddressEncryptedOptional = swap_init_payload.emailAddressEncryptedOptional
        atomic_swap_info.senderAddress = self.make_address_from_data(signer_pubkey)
        atomic_swap_info.senderAddressNonLocal = swap_init_payload.senderAddressNonLocal
        atomic_swap_info.receiverAddress = swap_init_payload.receiverAddress
        swap_address = self.make_address(atomic_swap_info.swapID)
        # Check if swap ID is already exist
        if get_data(context, AtomicSwapInfo, swap_address):
            raise InvalidTransaction('Atomic swap ID is already taken, please use a different one!')
        # end

        # 1. Ensure transaction was within an hour
        atomic_swap_info.secretLock = swap_init_payload.secretLockOptionalBob
        created_at = datetime.datetime.fromtimestamp(atomic_swap_info.timestamp)
        now = datetime.datetime.now()

        if not (now - datetime.timedelta(hours=1) < created_at < now):
            raise InvalidTransaction('Transaction is created a long time ago or timestamp is assigned set.')
        # END

        # 2. check weather the sender is Alice:
        genesis_members_str = _get_setting_value(context, SETTINGS_KEY_ALLOWED_GENESIS_MEMBERS)
        if not genesis_members_str:
            raise InvalidTransaction('REMchain is not configured to process atomic swaps.')

        genesis_members_list = genesis_members_str.split()
        sender_address = self.make_address_from_data(signer_pubkey)

        atomic_swap_info.isInitiator = sender_address not in genesis_members_list
        # END

        transfer_payload = TransferPayload()
        transfer_payload.address_to = atomic_swap_info.receiverAddress
        transfer_payload.amount = atomic_swap_info.amount
        token_updated_state = TokenHandler()._transfer_from_address(context, atomic_swap_info.senderAddress, transfer_payload)

        return {
            swap_address: atomic_swap_info
        }.update(token_updated_state)



