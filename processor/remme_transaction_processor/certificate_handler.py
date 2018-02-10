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
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from .helpers import *
from .certificate_pb2 import CertificateStorage

FAMILY_NAME = 'certificate'
FAMILY_VERSIONS = ['0.1']

CERT_ORGANIZATION = 'REMME'
CERT_MAX_VALIDITY = datetime.timedelta(365)


class CertificateHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def _save_certificate(self, context, transactor, certificate):
        certificate = x509.load_pem_x509_certificate(certificate_raw.encode(),
                                                     default_backend())
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
        fingerprint = certificate.fingerprint(hashes.SHA512()).hex()
        # TODO: consider passing just the binary representation of the certificate here
        address = self._make_address(fingerprint)
        data = CertificateStorage()
        data.hash = fingerprint
        data.owner = transactor
        data.revoked = False
        self._store_data(context, address, data)
    
    def _revoke_certificate(self, context, transactor, certificate_address):
        data = self._get_data(context, certificate_address, CertificateStorage)
        if data is None:
            raise InvalidTransaction('No such certificate.')
        if transactor != data.owner:
            raise InvalidTransaction('Only owner can revoke the certificate.')
        if data.revoked:
            raise InvalidTransaction('The certificate is already revoked.')
        data.revoked = True
        self._store_data(context, certificate_address, data)

    def apply(self, transaction, context):
        pass
