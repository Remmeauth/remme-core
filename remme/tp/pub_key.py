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
import binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.tp.basic import BasicHandler, get_data
from remme.tp.account import AccountHandler, get_account_by_address

from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload, RevokePubKeyPayload, PubKeyMethod
)
from remme.shared.singleton import singleton

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'pub_key'
FAMILY_VERSIONS = ['0.1']

CERT_ORGANIZATION = 'REMME'
CERT_MAX_VALIDITY_DAYS = 365
CERT_MAX_VALIDITY = datetime.timedelta(CERT_MAX_VALIDITY_DAYS)

CERT_STORE_PRICE = 10


@singleton
class PubKeyHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            PubKeyMethod.STORE: {
                'pb_class': NewPubKeyPayload,
                'processor': self._store_pub_key
            },
            PubKeyMethod.REVOKE: {
                'pb_class': RevokePubKeyPayload,
                'processor': self._revoke_pub_key
            }
        }

    def _store_pub_key(self, context, signer_pubkey, transaction_payload):
        address = self.make_address_from_data(transaction_payload.public_key)
        LOGGER.info('Cert address {}'.format(address))
        data = get_data(context, PubKeyStorage, address)
        if data:
            raise InvalidTransaction('This pub key is already registered.')

        cert_signer_pubkey = load_pem_public_key(transaction_payload.public_key.encode('utf-8'),
                                                 backend=default_backend())
        try:
            cert_signer_pubkey.verify(binascii.unhexlify(transaction_payload.entity_hash_signature),
                                      binascii.unhexlify(transaction_payload.entity_hash),
                                      padding.PKCS1v15(),
                                      # padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                      #             salt_length=padding.PSS.MAX_LENGTH),
                                      hashes.SHA512())
        except InvalidSignature:
            raise InvalidTransaction('Invalid signature')
        except binascii.Error:
            LOGGER.debug(f'entity_hash_signature {transaction_payload.entity_hash_signature}')
            LOGGER.debug(f'entity_hash {transaction_payload.entity_hash}')
            raise InvalidTransaction('Entity hash or signature not a hex format')

        data = PubKeyStorage()
        data.owner = signer_pubkey
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        account_address = AccountHandler.make_address_from_data(signer_pubkey)
        account = get_account_by_address(context, account_address)
        if account.balance < CERT_STORE_PRICE:
            raise InvalidTransaction('Not enough tokens to register a new pub key. Current balance: {}'
                                     .format(account.balance))
        account.balance -= CERT_STORE_PRICE

        if address not in account.pub_keys:
            account.pub_keys.append(address)

        return {address: data,
                account_address: account}

    def _revoke_pub_key(self, context, signer_pubkey, transaction_payload):
        data = get_data(context, PubKeyStorage, transaction_payload.address)
        if data is None:
            raise InvalidTransaction('No such pub key.')
        if signer_pubkey != data.owner:
            raise InvalidTransaction('Only owner can revoke the pub key.')
        if data.revoked:
            raise InvalidTransaction('The pub key is already revoked.')
        data.revoked = True

        LOGGER.info('Revoked the pub_key on address {}'.format(transaction_payload.address))

        return {transaction_payload.address: data}
