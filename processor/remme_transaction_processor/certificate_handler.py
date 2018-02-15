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
import hashlib
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptogrphy.exceptions import InvalidSignature
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_signing.secp256k1 import Secp256k1PublicKey, Secp256k1Context
from .helpers import *
from processor.protos.certificate_pb2 import CertificateStorage

FAMILY_NAME = 'certificate'
FAMILY_VERSIONS = ['0.1']

CERT_ORGANIZATION = 'REMME'
CERT_MAX_VALIDITY = datetime.timedelta(365)


class CertificateHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def _save_certificate(self, data, transactor, certificate_raw, signature_rem, signature_crt):
        certificate = x509.load_pem_x509_certificate(certificate_raw.encode(),
                                                     default_backend())

        if data is not None:
            InvalidTransaction('The certificate is already registered')

        certificate_pubkey = certificate.public_key()
        try:
            certificate_pubkey.verify(signature_crt, signature_rem, hashes.SHA512())
        except InvalidSignature:
            raise InvalidTransaction('signature_crt mismatch')

        sawtooth_signing_ctx = Secp256k1Context()
        sawtooth_signing_pubkey = Secp256k1PublicKey(transactor)
        sawtooth_signing_check_res = \
            sawtooth_signing_ctx.verify(signature_rem,
                                        hashlib.sha512(certificate_raw.encode('utf-8')).hexdigest(),
                                        sawtooth_signing_pubkey)
        if not sawtooth_signing_check_res:
            raise InvalidTransaction('signature_rem mismatch')

        subject = certificate.subject
        organization = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        uid = subject.get_attributes_for_oid(NameOID.USER_ID)
        valid_from = certificate.not_valid_before
        valid_until = certificate.not_valid_after

        if organization != CERT_ORGANIZATION:
            raise InvalidTransaction('The organization name should be set to REMME.')
        if uid != transactor:
            raise InvalidTransaction('The certificate should be sent by its signer.')
        if subject != certificate.issuer:
            raise InvalidTransaction('Expecting a self-signed certificate.')
        if valid_until - valid_from > CERT_MAX_VALIDITY:
            raise InvalidTransaction('The certificate validity exceeds the maximum value.')

        fingerprint = certificate.fingerprint(hashes.SHA512()).hex()[:64]
        address = self.make_address(fingerprint)
        data = CertificateStorage()
        data.hash = fingerprint
        data.owner = transactor
        data.revoked = False

        return data

    def _revoke_certificate(self, data, transactor, certificate_address):
        if data is None:
            raise InvalidTransaction('No such certificate.')
        if transactor != data.owner:
            raise InvalidTransaction('Only owner can revoke the certificate.')
        if data.revoked:
            raise InvalidTransaction('The certificate is already revoked.')
        data.revoked = True

        return data

    def apply(self, transaction, context):
        pass
