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
import hashlib
import abc

import ed25519
import secp256k1
from secp256k1 import lib

from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_der_public_key
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.settings import ZERO_ADDRESS
from remme.tp.basic import (
    BasicHandler, get_data, get_multiple_data, PB_CLASS, PROCESSOR,
    VALIDATOR,
)
from remme.tp.account import AccountHandler

from remme.protos.account_pb2 import Account, TransferPayload
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload,
    RevokePubKeyPayload,
    PubKeyMethod,
)
from remme.settings.helper import _get_setting_value
from remme.shared.forms import NewPublicKeyPayloadForm, RevokePubKeyPayloadForm

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'pub_key'
FAMILY_VERSIONS = ['0.1']

PUB_KEY_ORGANIZATION = 'REMME'
PUB_KEY_MAX_VALIDITY = timedelta(365)
PUB_KEY_STORE_PRICE = 10

ECONOMY_IS_ENABLED_VALUE = 'true'


def detect_processor_cls(config):
    if isinstance(config, NewPubKeyPayload.RSAConfiguration):
        return RSAProcessor
    elif isinstance(config, NewPubKeyPayload.ECDSAConfiguration):
        return ECDSAProcessor
    elif isinstance(config, NewPubKeyPayload.Ed25519Configuration):
        return Ed25519Processor
    raise NotImplementedError


class BasePubKeyProcessor(metaclass=abc.ABCMeta):

    def __init__(self, entity_hash, entity_hash_signature,
                 valid_from, valid_to, hashing_algorithm, config):
        self._entity_hash = entity_hash
        self._entity_hash_signature = entity_hash_signature
        self._valid_from = valid_from
        self._valid_to = valid_to
        self._hashing_algorithm = hashing_algorithm
        self._config = config

    @abc.abstractmethod
    def get_hashing_algorithm(self):
        """Return libriary special algoritm in according to protobuf
        """

    def get_public_key(self):
        """Get public key from given signature or points
        """
        return self._config.key

    @abc.abstractmethod
    def verify(self):
        """Verify if signature was successfull
        """


class RSAProcessor(BasePubKeyProcessor):

    def verify(self):
        try:
            verifier = load_der_public_key(self.get_public_key(),
                                           default_backend())
        except ValueError as e:
            raise InvalidTransaction(
                'Cannot deserialize the provided public key. '
                'Check if it is in DER format.')

        try:
            verifier.verify(self._entity_hash_signature, self._entity_hash,
                            self.get_padding(), self.get_hashing_algorithm()())
            return True
        except InvalidSignature:
            return False

    def get_hashing_algorithm(self):
        alg_name = NewPubKeyPayload.HashingAlgorithm \
            .Name(self._hashing_algorithm)
        return getattr(hashes, alg_name)

    def get_padding(self):
        Padding = NewPubKeyPayload.RSAConfiguration.Padding
        if self._config.padding == Padding.Value('PSS'):
            return padding.PSS(mgf=padding.MGF1(self.get_hashing_algorithm()()),
                               salt_length=padding.PSS.MAX_LENGTH)
        elif self._config.padding == Padding.Value('PKCS1v15'):
            return padding.PKCS1v15()
        else:
            raise NotImplementedError('Unsupported RSA padding')


class ECDSAProcessor(BasePubKeyProcessor):

    def verify(self):
        try:
            pub_key = secp256k1.PublicKey()
            pub_key.deserialize(self.get_public_key())

            assert pub_key.public_key, "No public key defined"

            if pub_key.flags & lib.SECP256K1_CONTEXT_VERIFY != \
               lib.SECP256K1_CONTEXT_VERIFY:
                raise Exception("instance not configured for sig verification")

            msg_digest = self.get_hashing_algorithm()(
                self._entity_hash).digest()
            raw_sig = pub_key.ecdsa_deserialize_compact(
                self._entity_hash_signature)

            verified = lib.secp256k1_ecdsa_verify(
                pub_key.ctx, raw_sig, msg_digest, pub_key.public_key)
        except Exception as e:
            LOGGER.exception(e)
            return False
        else:
            return bool(verified)

    def get_hashing_algorithm(self):
        alg_name = NewPubKeyPayload.HashingAlgorithm \
            .Name(self._hashing_algorithm).lower()
        return getattr(hashlib, alg_name)

    def get_curve_type(self):
        raise NotImplementedError


class Ed25519Processor(BasePubKeyProcessor):

    def verify(self):
        verifier = ed25519.VerifyingKey(self.get_public_key())
        msg_digest = self.get_hashing_algorithm()(self._entity_hash).digest()
        try:
            verifier.verify(self._entity_hash_signature, msg_digest)
            return True
        except ed25519.BadSignatureError:
            return False

    def get_hashing_algorithm(self):
        alg_name = NewPubKeyPayload.HashingAlgorithm \
            .Name(self._hashing_algorithm).lower()
        return getattr(hashlib, alg_name)


class PubKeyHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            PubKeyMethod.STORE: {
                PB_CLASS: NewPubKeyPayload,
                PROCESSOR: self._store_pub_key,
                VALIDATOR: NewPublicKeyPayloadForm,
            },
            PubKeyMethod.REVOKE: {
                PB_CLASS: RevokePubKeyPayload,
                PROCESSOR: self._revoke_pub_key,
                VALIDATOR: RevokePubKeyPayloadForm,
            }
        }

    @staticmethod
    def _is_public_key_validity_exceeded(valid_from, valid_to):
        """
        Check if public key validity exceeds the maximum value.
        Public key validity maximum value in one year (365 days).
        """
        valid_from = datetime.fromtimestamp(valid_from)
        valid_to = datetime.fromtimestamp(valid_to)

        if valid_to - valid_from > PUB_KEY_MAX_VALIDITY:
            return False

        return True

    @staticmethod
    def _charge_tokens_for_storing(context, address_from, address_to):
        """
        Send fixed tokens value from address that want to store public key to node's storage address.
        """
        transfer_payload = TransferPayload()
        transfer_payload.address_to = address_to
        transfer_payload.value = PUB_KEY_STORE_PRICE

        transfer_state = AccountHandler()._transfer_from_address(
            context=context, address_from=address_from, transfer_payload=transfer_payload,
        )

        return transfer_state

    def _store_pub_key(self, context, signer_pubkey, transaction_payload):
        """
        Store public key to the blockchain.
        Flow on client:
        1. Create private and public key (for instance, RSA).
        2. Create random data and sign it with private key to allows node verify signature,
            so ensure the address sent transaction is a real owner of public key.
        3. Send public key, signature, and other information to the node.
        Node does checks: if public key already exists in the blockchain, try to deserialize public key,
        try to verify signature, if validity exceeds.
        If transaction successfully passed checks, node charges fixed tokens price for storing
        public keys (if node economy is enabled) and link public key to the account (address).
        References:
            - https://docs.remme.io/remme-core/docs/family-pub-key.html
            - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_public_key_storage.py
        """
        conf_name = transaction_payload.WhichOneof('configuration')
        if not conf_name:
            raise InvalidTransaction('Configuration for public key not set')

        conf_payload = getattr(transaction_payload, conf_name)

        processor_cls = detect_processor_cls(conf_payload)
        processor = processor_cls(transaction_payload.entity_hash,
                                  transaction_payload.entity_hash_signature,
                                  transaction_payload.valid_from,
                                  transaction_payload.valid_to,
                                  transaction_payload.hashing_algorithm,
                                  conf_payload)

        public_key = processor.get_public_key()

        public_key_to_store_address = self.make_address_from_data(public_key)
        LOGGER.info('Public key address {}'.format(public_key_to_store_address))

        sender_account_address = AccountHandler() \
            .make_address_from_data(signer_pubkey)
        LOGGER.info('Account address {}'.format(sender_account_address))
        data, account = get_multiple_data(context, [
            (public_key_to_store_address, PubKeyStorage),
            (sender_account_address, Account),
        ])
        if data:
            raise InvalidTransaction('This public key is already registered.')

        sig_is_valid = processor.verify()
        if sig_is_valid is False:
            raise InvalidTransaction('Invalid signature')

        if not self._is_public_key_validity_exceeded(
            valid_from=transaction_payload.valid_from,
            valid_to=transaction_payload.valid_to
        ):
            raise InvalidTransaction('The public key validity exceeds '
                                     'the maximum value.')

        data = PubKeyStorage()
        data.owner = signer_pubkey
        data.payload.CopyFrom(transaction_payload)
        data.is_revoked = False

        if not account:
            account = Account()

        state = {
            sender_account_address: account,
            public_key_to_store_address: data
        }

        is_economy_enabled = _get_setting_value(context,
                                                'remme.economy_enabled',
                                                'true').lower()
        if is_economy_enabled == 'true':

            if ZERO_ADDRESS != sender_account_address:

                transfer_state = self._charge_tokens_for_storing(
                    context=context, address_from=sender_account_address,
                    address_to=ZERO_ADDRESS,
                )

                state.update(transfer_state)
                account = transfer_state[sender_account_address]

        if public_key_to_store_address not in account.pub_keys:
            account.pub_keys.append(public_key_to_store_address)

        return state

    @staticmethod
    def _revoke_pub_key(context, signer_pubkey, revoke_pub_key_payload):
        public_key_information = get_data(context, PubKeyStorage, revoke_pub_key_payload.address)

        if public_key_information is None:
            raise InvalidTransaction('No public key is presented in chain.')

        if signer_pubkey != public_key_information.owner:
            raise InvalidTransaction('Only owner can revoke the public key.')

        if public_key_information.is_revoked:
            raise InvalidTransaction('The public key is already revoked.')

        public_key_information.is_revoked = True
        LOGGER.info('Revoked the pub key on address {}'.format(revoke_pub_key_payload.address))

        return {
            revoke_pub_key_payload.address: public_key_information,
        }
