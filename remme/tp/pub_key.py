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
import binascii
from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.settings import SETTINGS_KEY_TO_GET_STORAGE_PUBLIC_KEY_BY
from remme.tp.basic import BasicHandler, get_data, get_multiple_data, PB_CLASS, PROCESSOR
from remme.tp.account import AccountHandler

from remme.protos.account_pb2 import (
    Account,
    TransferPayload,
)
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload,
    RevokePubKeyPayload,
    PubKeyMethod,
)
from remme.settings.helper import _get_setting_value

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'pub_key'
FAMILY_VERSIONS = ['0.1']

PUB_KEY_ORGANIZATION = 'REMME'

# Backward compatibility to use more obvious variables name
CERTIFICATE_PUBLIC_KEY_MAXIMUM_VALIDITY = PUB_KEY_MAX_VALIDITY = timedelta(365)
CERTIFICATE_PUBLIC_KEY_STORE_PRICE = PUB_KEY_STORE_PRICE = 10

ECONOMY_IS_ENABLED_VALUE = 'true'


class PubKeyHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            PubKeyMethod.STORE: {
                PB_CLASS: NewPubKeyPayload,
                PROCESSOR: self._store_pub_key
            },
            PubKeyMethod.REVOKE: {
                PB_CLASS: RevokePubKeyPayload,
                PROCESSOR: self._revoke_pub_key
            }
        }

    @staticmethod
    def _is_signature_valid(certificate_public_key, ehs_bytes, eh_bytes):
        # FIXME: For support PKCS1v15 and PSS
        LOGGER.warning('HAZARD: Detecting padding for verification')
        sigerr = 0
        pkcs = padding.PKCS1v15()
        pss = padding.PSS(mgf=padding.MGF1(hashes.SHA512()), salt_length=padding.PSS.MAX_LENGTH)
        for _padding in (pkcs, pss):
            try:
                certificate_public_key.verify(ehs_bytes, eh_bytes, _padding, hashes.SHA512())
                LOGGER.warning('HAZARD: Padding found: %s', _padding.name)
            except InvalidSignature:
                sigerr += 1

        if sigerr == 2:
            return False

        return True

    @staticmethod
    def _is_certificate_validity_exceeded(valid_from, valid_to):
        """
        Check if certificate validity exceeds the maximum value.

        Certificate public key validity maximum value in one year (365 days).
        """
        valid_from = datetime.fromtimestamp(valid_from)
        valid_to = datetime.fromtimestamp(valid_to)

        if valid_to - valid_from > CERTIFICATE_PUBLIC_KEY_MAXIMUM_VALIDITY:
            return False

        return True

    @staticmethod
    def _charge_tokens_for_storing(context, address_from, address_to):
        """
        Send fixed tokens value from address that want to store certificate public key to node's storage address.
        """
        transfer_payload = TransferPayload()
        transfer_payload.address_to = address_to
        transfer_payload.value = PUB_KEY_STORE_PRICE

        transfer_state = AccountHandler()._transfer_from_address(
            context=context, address_from=address_from, transfer_payload=transfer_payload,
        )

        return transfer_state

    def _store_pub_key(self, context, signer_public_key, new_public_key_payload):
        """
        Store certificate public key to the blockchain.

        Flow on client:
        1. Create certificate private and public key (for instance, RSA).
        2. Create random data and sign it with certificate private key to allows node verify signature,
            so ensure the address sent transaction is a real owner of certificate public key.
        3. Send certificate public key, signature, and other information to the node.

        Node does checks: if public key already exists in the blockchain, try to deserialize public key,
        try to verify signature, if validity exceeds.

        If transaction successfully passed checks, node charges fixed tokens price for storing
        certificate public keys (if node economy is enabled) and link public key to the account (address).

        References:
            - https://docs.remme.io/remme-core/docs/family-pub-key.html
            - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_public_key_storage.py
        """
        public_key_to_store_address = self.make_address_from_data(new_public_key_payload.public_key)
        sender_account_address = AccountHandler().make_address_from_data(signer_public_key)

        public_key_information, account = get_multiple_data(context, [
            (public_key_to_store_address, PubKeyStorage),
            (sender_account_address, Account),
        ])

        if public_key_information:
            raise InvalidTransaction('This public key is already registered.')

        try:
            certificate_public_key = load_pem_public_key(
                new_public_key_payload.public_key.encode('utf-8'), backend=default_backend(),
            )

        except ValueError:
            raise InvalidTransaction('Cannot deserialize the provided public key. Check if it is in PEM format.')

        try:
            ehs_bytes = binascii.unhexlify(new_public_key_payload.entity_hash_signature)
            eh_bytes = binascii.unhexlify(new_public_key_payload.entity_hash)
        except binascii.Error:
            raise InvalidTransaction('Entity hash or/and signature is not a hex format.')

        if not self._is_signature_valid(
                certificate_public_key=certificate_public_key, ehs_bytes=ehs_bytes, eh_bytes=eh_bytes,
        ):
            raise InvalidTransaction('Invalid signature.')

        certificate_valid_from, certificate_valid_to = \
            new_public_key_payload.valid_from, new_public_key_payload.valid_to

        if not self._is_certificate_validity_exceeded(valid_from=certificate_valid_from, valid_to=certificate_valid_to):
            raise InvalidTransaction('The public key validity exceeds the maximum value.')

        public_key_to_store = PubKeyStorage()
        public_key_to_store.owner = signer_public_key
        public_key_to_store.payload.CopyFrom(new_public_key_payload)
        public_key_to_store.revoked = False

        if not account:
            account = Account()

        state = {
            sender_account_address: account,
            public_key_to_store_address: public_key_to_store,
        }

        is_economy_enabled = _get_setting_value(context, 'remme.economy_enabled', 'true').lower()

        if is_economy_enabled == ECONOMY_IS_ENABLED_VALUE:

            storage_public_key = _get_setting_value(context, SETTINGS_KEY_TO_GET_STORAGE_PUBLIC_KEY_BY)

            if not storage_public_key:
                raise InvalidTransaction('The node\'s storage public key hasn\'t been set, get node config to ensure.')

            storage_address = AccountHandler().make_address_from_data(storage_public_key)

            if storage_address != sender_account_address:

                transfer_state = self._charge_tokens_for_storing(
                    context=context, address_from=sender_account_address, address_to=storage_address,
                )

                # If sender account allows, make payment and push account protobuf to state
                # to be updated with related public key below.
                state.update(transfer_state)
                account = transfer_state.get(sender_account_address)

        if public_key_to_store_address not in account.pub_keys:
            account.pub_keys.append(public_key_to_store_address)

        return state

    @staticmethod
    def _revoke_pub_key(context, signer_pubkey, revoke_pub_key_payload):
        public_key_information = get_data(context, PubKeyStorage, revoke_pub_key_payload.address)

        if public_key_information is None:
            raise InvalidTransaction('No certificate public key is presented in chain.')

        if signer_pubkey != public_key_information.owner:
            raise InvalidTransaction('Only owner can revoke the public key.')

        if public_key_information.revoked:
            raise InvalidTransaction('The public key is already revoked.')

        public_key_information.revoked = True
        LOGGER.info('Revoked the pub key on address {}'.format(revoke_pub_key_payload.address))

        return {
            revoke_pub_key_payload.address: public_key_information,
        }
