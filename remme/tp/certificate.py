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

from remme.shared.basic_handler import BasicHandler, get_data
from remme.tp.account import AccountHandler

from remme.shared.utils import hash512

from remme.protos.certificate_pb2 import CertificateStorage, \
    NewCertificatePayload, RevokeCertificatePayload, CertificateMethod
from remme.shared.singleton import singleton

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'certificate'
FAMILY_VERSIONS = ['0.1']

CERT_ORGANIZATION = 'REMME'
CERT_MAX_VALIDITY_DAYS = 365
CERT_MAX_VALIDITY = datetime.timedelta(CERT_MAX_VALIDITY_DAYS)

CERT_STORE_PRICE = 10


@singleton
class CertificateHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            CertificateMethod.STORE: {
                'pb_class': NewCertificatePayload,
                'processor': self._store_certificate
            },
            CertificateMethod.REVOKE: {
                'pb_class': RevokeCertificatePayload,
                'processor': self._revoke_certificate
            }
        }

    def _store_certificate(self, context, signer_pubkey, transaction_payload):
        address = self.make_address_from_data(transaction_payload.certificate_raw)
        LOGGER.info('Cert address {}'.format(address))
        data = get_data(context, CertificateStorage, address)
        if data:
            raise InvalidTransaction('This certificate is already registered.')

        certificate = x509.load_der_x509_certificate(bytes.fromhex(transaction_payload.certificate_raw),
                                                     default_backend())

        if transaction_payload.cert_signer_public_key:
            cert_signer_pubkey = load_pem_public_key(transaction_payload.cert_signer_public_key.encode('utf-8'),
                                                     backend=default_backend())
        else:
            cert_signer_pubkey = certificate.public_key()

        try:
            cert_signer_pubkey.verify(bytes.fromhex(transaction_payload.signature_crt),
                                      bytes.fromhex(transaction_payload.signature_rem),
                                      padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                  salt_length=padding.PSS.MAX_LENGTH),
                                      hashes.SHA256())
        except InvalidSignature:
            raise InvalidTransaction('signature_crt mismatch')

        crt_hash = hash512(transaction_payload.certificate_raw).encode('utf-8')
        sawtooth_signing_ctx = Secp256k1Context()
        sawtooth_signing_pubkey = Secp256k1PublicKey.from_hex(signer_pubkey)
        sawtooth_signing_check_res = \
            sawtooth_signing_ctx.verify(transaction_payload.signature_rem,
                                        crt_hash,
                                        sawtooth_signing_pubkey)
        if not sawtooth_signing_check_res:
            raise InvalidTransaction('signature_rem mismatch with signer key {}'.format(signer_pubkey))

        subject = certificate.subject
        issuer = certificate.issuer

        organization = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
        uid = issuer.get_attributes_for_oid(NameOID.USER_ID)[0].value
        valid_from = certificate.not_valid_before
        valid_until = certificate.not_valid_after

        if organization != CERT_ORGANIZATION:
            raise InvalidTransaction('The organization name should be set to REMME. The actual name is {}'
                                     .format(organization))
        if uid != signer_pubkey:
            raise InvalidTransaction('The certificate should be sent by its signer. Certificate signed by {}. '
                                     'Transaction sent by {}.'.format(uid, signer_pubkey))

        if valid_until - valid_from > CERT_MAX_VALIDITY:
            raise InvalidTransaction('The certificate validity exceeds the maximum value.')

        fingerprint = certificate.fingerprint(hashes.SHA512()).hex()[:64]
        data = CertificateStorage()
        data.hash = fingerprint
        data.owner = signer_pubkey
        data.revoked = False

        account_address = AccountHandler.make_address_from_data(signer_pubkey)
        account = get_account_by_address(context, account_address)
        if account.balance < CERT_STORE_PRICE:
            raise InvalidTransaction('Not enough tokens to register a new certificate. Current balance: {}'
                                     .format(account.balance))
        account.balance -= CERT_STORE_PRICE

        if address not in account.certificates:
            account.certificates.append(address)

        LOGGER.info('Registered a new certificate on address {}. Fingerprint: {}. Pub key: {}.'.format(address, fingerprint, signer_pubkey))

        return {address: data,
                account_address: account}

    def _revoke_certificate(self, context, signer_pubkey, transaction_payload):
        data = get_data(context, CertificateStorage, transaction_payload.address)
        if data is None:
            raise InvalidTransaction('No such certificate.')
        if signer_pubkey != data.owner:
            raise InvalidTransaction('Only owner can revoke the certificate.')
        if data.revoked:
            raise InvalidTransaction('The certificate is already revoked.')
        data.revoked = True

        LOGGER.info('Revoked the certificate on address {}'.format(transaction_payload.address))

        return {transaction_payload.address: data}
