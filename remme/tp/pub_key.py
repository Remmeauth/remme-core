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

from remme.settings import SETTINGS_STORAGE_PUB_KEY
from remme.tp.basic import BasicHandler, get_data, get_multiple_data, PB_CLASS, PROCESSOR
from remme.tp.account import AccountHandler

from remme.protos.account_pb2 import Account
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload, RevokePubKeyPayload, PubKeyMethod
)
from remme.settings.helper import _get_setting_value

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'pub_key'
FAMILY_VERSIONS = ['0.1']

PUB_KEY_ORGANIZATION = 'REMME'
PUB_KEY_MAX_VALIDITY = timedelta(365)
PUB_KEY_STORE_PRICE = 10


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

    def _store_pub_key(self, context, signer_pubkey, transaction_payload):
        address = self.make_address_from_data(transaction_payload.public_key)
        LOGGER.info('Pub key address {}'.format(address))

        account_address = AccountHandler().make_address_from_data(signer_pubkey)
        LOGGER.info('Account address {}'.format(address))
        data, account = get_multiple_data(context, [(address, PubKeyStorage), (account_address, Account)])
        if data:
            raise InvalidTransaction('This pub key is already registered.')

        cert_signer_pubkey = load_pem_public_key(transaction_payload.public_key.encode('utf-8'),
                                                 backend=default_backend())
        try:
            ehs_bytes = binascii.unhexlify(transaction_payload.entity_hash_signature)
            eh_bytes = binascii.unhexlify(transaction_payload.entity_hash)
        except binascii.Error:
            LOGGER.debug(f'entity_hash_signature {transaction_payload.entity_hash_signature}')
            LOGGER.debug(f'entity_hash {transaction_payload.entity_hash}')
            raise InvalidTransaction('Entity hash or signature not a hex format')

        # FIXME: For support PKCS1v15 and PSS
        LOGGER.warn('HAZARD: Detecting padding for verification')
        sigerr = 0
        pkcs = padding.PKCS1v15()
        pss = padding.PSS(mgf=padding.MGF1(hashes.SHA512()), salt_length=padding.PSS.MAX_LENGTH)
        for _padding in (pkcs, pss):
            try:
                cert_signer_pubkey.verify(ehs_bytes, eh_bytes, _padding, hashes.SHA512())
                LOGGER.warn('HAZARD: Padding found: %s', _padding.name)
            except InvalidSignature:
                sigerr += 1

        if sigerr == 2:
            raise InvalidTransaction('Invalid signature')

        valid_from = datetime.fromtimestamp(transaction_payload.valid_from)
        valid_to = datetime.fromtimestamp(transaction_payload.valid_to)

        if valid_to - valid_from > PUB_KEY_MAX_VALIDITY:
            raise InvalidTransaction('The public key validity exceeds the maximum value.')

        data = PubKeyStorage()
        data.owner = signer_pubkey
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        if not account:
            account = Account()

        state = {account_address: account, address: data}
        is_economy_enabled = _get_setting_value(context,
                                                'remme.economy_enabled',
                                                'true').lower()
        if is_economy_enabled == 'true':
            storage_pub_key = _get_setting_value(context,
                                                 SETTINGS_STORAGE_PUB_KEY)
            if not storage_pub_key:
                raise InvalidTransaction('The storage public key not set.')

            storage_address = AccountHandler() \
                .make_address_from_data(storage_pub_key)

            if storage_address != account_address:
                transfer_state = AccountHandler() \
                    .create_transfer(context, account_address, storage_address,
                                     PUB_KEY_STORE_PRICE)
                state.update(transfer_state)
                # update account from transfer state
                account = transfer_state[account_address]

        if address not in account.pub_keys:
            account.pub_keys.append(address)

        return state

    def _revoke_pub_key(self, context, signer_pubkey, transaction_payload):
        data = get_data(context, PubKeyStorage, transaction_payload.address)
        if data is None:
            raise InvalidTransaction('No such pub key.')
        if signer_pubkey != data.owner:
            raise InvalidTransaction('Only owner can revoke the pub key.')
        if data.revoked:
            raise InvalidTransaction('The pub key is already revoked.')
        data.revoked = True

        LOGGER.info('Revoked the pub key on address {}'.format(transaction_payload.address))

        return {transaction_payload.address: data}
