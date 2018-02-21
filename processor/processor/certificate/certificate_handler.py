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

import cbor
import datetime
import logging
import hashlib
import secp256k1
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_signing.secp256k1 import Secp256k1PublicKey, Secp256k1Context
from processor.shared.basic_handler import *
from processor.protos.certificate_pb2 import CertificateStorage, CertificateTransaction

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'certificate'
FAMILY_VERSIONS = ['0.1']

CERT_ORGANIZATION = 'REMME'
CERT_MAX_VALIDITY = datetime.timedelta(365)


class CertificateHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)
        LOGGER.info('Started certificates operations transactions handler.')

    def apply(self, transaction, context):
        super().process_apply(transaction, context, CertificateTransaction)

    def make_address(self, appendix):
        return self._prefix + appendix

    def process_state(self, signer_pubkey, signer, payload, state):
        transaction = CertificateTransaction()
        payload_decoded = cbor.loads(payload)
        transaction.ParseFromString(payload_decoded['data'])
        if transaction.type == CertificateTransaction.CREATE:
            appendix = hashlib.sha512(transaction.certificate_raw.encode('utf-8')).hexdigest()[0:64]
            raw_data = self.context.get_state([self._prefix + appendix])
            stored_data = CertificateStorage()
            if isinstance(raw_data, list):
                if len(raw_data) > 0:
                    stored_data.ParseFromString(raw_data[0].data)
            data = self._save_certificate(stored_data,
                                          signer,
                                          signer_pubkey,
                                          transaction.certificate_raw,
                                          transaction.signature_rem,
                                          transaction.signature_crt,
                                          self._prefix + appendix)
            return data
        elif transaction.type == CertificateTransaction.REVOKE:
            appendix = transaction.address
            raw_data = self.context.get_state([appendix])
            stored_data = CertificateStorage()
            if isinstance(raw_data, list):
                if len(raw_data) > 0:
                    stored_data.ParseFromString(raw_data[0].data)
                else:
                    InvalidTransaction('No certificate in the given address')
            data = self._revoke_certificate(stored_data, signer, appendix)
            return data
        else:
            raise InvalidTransaction('Unknown value {} for the certificate operation type.'.
                                     format(int(transaction.type)))

    def _save_certificate(self, data, transactor, transactor_pubkey, certificate_raw, signature_rem, signature_crt, address):
        certificate = x509.load_der_x509_certificate(bytes.fromhex(certificate_raw),
                                                     default_backend())
        if data is not None:
            InvalidTransaction('The certificate is already registered')

        certificate_pubkey = certificate.public_key()
        try:
            certificate_pubkey.verify(bytes.fromhex(signature_crt),
                                      bytes.fromhex(signature_rem),
                                      padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                  salt_length=padding.PSS.MAX_LENGTH),
                                      hashes.SHA256())
        except InvalidSignature:
            raise InvalidTransaction('signature_crt mismatch')

        sawtooth_signing_ctx = Secp256k1Context()
        sawtooth_signing_pubkey = Secp256k1PublicKey.from_hex(transactor_pubkey)
        sawtooth_signing_check_res = \
            sawtooth_signing_ctx.verify(signature_rem,
                                        hashlib.sha512(certificate_raw.encode('utf-8')).hexdigest().encode('utf-8'),
                                        sawtooth_signing_pubkey)
        if not sawtooth_signing_check_res:
            raise InvalidTransaction('signature_rem mismatch with signer key {}'.format(transactor_pubkey))

        subject = certificate.subject
        organization = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
        uid = subject.get_attributes_for_oid(NameOID.USER_ID)[0].value
        valid_from = certificate.not_valid_before
        valid_until = certificate.not_valid_after

        if organization != CERT_ORGANIZATION:
            raise InvalidTransaction('The organization name should be set to REMME. The actual name is {}'.format(organization))
        if uid != transactor:
            raise InvalidTransaction('The certificate should be sent by its signer. Certificate signed by {}. Transaction sent by {}.'.format(uid, transactor))
        if subject != certificate.issuer:
            raise InvalidTransaction('Expecting a self-signed certificate.')
        if valid_until - valid_from > CERT_MAX_VALIDITY:
            raise InvalidTransaction('The certificate validity exceeds the maximum value.')
        fingerprint = certificate.fingerprint(hashes.SHA512()).hex()[:64]
        data.hash = fingerprint
        data.owner = transactor
        data.revoked = False

        return {address: data}

    def _revoke_certificate(self, data, transactor, certificate_address):
        if data is None:
            raise InvalidTransaction('No such certificate.')
        if transactor != data.owner:
            raise InvalidTransaction('Only owner can revoke the certificate.')
        if data.revoked:
            raise InvalidTransaction('The certificate is already revoked.')
        data.revoked = True

        return {certificate_address: data}
