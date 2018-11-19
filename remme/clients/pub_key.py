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
import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload, RevokePubKeyPayload, PubKeyMethod
)
from remme.clients.basic import BasicClient
from remme.tp.pub_key import PubKeyHandler
from remme.tp.account import AccountHandler
from remme.tp.pub_key import PUB_KEY_ORGANIZATION, PUB_KEY_MAX_VALIDITY
from remme.settings.helper import _make_settings_key
from remme.settings import SETTINGS_STORAGE_PUB_KEY
from remme.shared.utils import hash512

from cryptography.x509.oid import NameOID
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


LOGGER = logging.getLogger(__name__)


class PubKeyClient(BasicClient):
    def __init__(self):
        super().__init__(PubKeyHandler)

    @classmethod
    def get_new_pub_key_payload(self, public_key, entity_hash, entity_hash_signature, valid_from, valid_to,
                                public_key_type=NewPubKeyPayload.RSA, entity_type=NewPubKeyPayload.PERSONAL):
        payload = NewPubKeyPayload()
        payload.public_key = public_key
        payload.public_key_type = public_key_type
        payload.entity_type = entity_type
        payload.entity_hash = entity_hash
        payload.entity_hash_signature = entity_hash_signature
        payload.valid_from = valid_from
        payload.valid_to = valid_to

        return payload

    @classmethod
    def get_revoke_payload(self, crt_address):
        payload = RevokePubKeyPayload()
        payload.address = crt_address

        return payload

    @staticmethod
    def get_encryption_algorithm(payload):
        encryption_algorithm = serialization.NoEncryption()
        if 'passphrase' in payload.keys():
            if payload['passphrase']:
                encryption_algorithm = serialization.BestAvailableEncryption(
                    payload['passphrase'].encode('utf-8'))
        return encryption_algorithm

    @staticmethod
    def generate_key():
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    @staticmethod
    def generate_key_export(key, encryption_algorithm):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption_algorithm
        )

    @staticmethod
    def get_params():
        return {
            'country_name': NameOID.COUNTRY_NAME,
            'state_name': NameOID.STATE_OR_PROVINCE_NAME,
            'street_address': NameOID.STREET_ADDRESS,
            'postal_address': NameOID.POSTAL_ADDRESS,
            'postal_code': NameOID.POSTAL_CODE,
            'locality_name': NameOID.LOCALITY_NAME,
            'common_name': NameOID.COMMON_NAME,
            'name': NameOID.GIVEN_NAME,
            'surname': NameOID.SURNAME,
            'pseudonym': NameOID.PSEUDONYM,
            'business_category': NameOID.BUSINESS_CATEGORY,
            'title': NameOID.TITLE,
            'email': NameOID.EMAIL_ADDRESS,
            'serial': NameOID.SERIAL_NUMBER,
            'generation_qualifier': NameOID.GENERATION_QUALIFIER
        }

    @staticmethod
    def get_dates_from_payload(payload):
        if 'validity_after' in payload:
            not_valid_before = datetime.datetime.utcnow() + datetime.timedelta(days=payload['validity_after'])
        else:
            not_valid_before = datetime.datetime.utcnow()

        if 'validity' in payload:
            not_valid_after = not_valid_before + datetime.timedelta(days=payload['validity'])
        else:
            not_valid_after = not_valid_before + PUB_KEY_MAX_VALIDITY

        return not_valid_before, not_valid_after

    @classmethod
    def create_certificate(cls, payload, org_name=PUB_KEY_ORGANIZATION, signer=None):
        parameters = cls.get_params()
        encryption_algorithm = cls.get_encryption_algorithm(payload)

        key = cls.generate_key()
        key_export = cls.generate_key_export(key, encryption_algorithm)

        if not signer:
            signer = PubKeyClient().get_signer()
        cert = cls.build_certificate(parameters, payload, key, signer.get_public_key().as_hex(), org_name)

        return cert, key, key_export

    @classmethod
    def build_certificate(cls, parameters, payload, key, signer_pub_key, org_name):
        name_oid = [x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
                    x509.NameAttribute(NameOID.USER_ID, signer_pub_key)]

        for k, v in parameters.items():
            if k in payload.keys():
                name_oid.append(x509.NameAttribute(v, payload[k]))

        subject = issuer = x509.Name(name_oid)

        not_valid_before, not_valid_after = cls.get_dates_from_payload(payload)

        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            not_valid_before
        ).not_valid_after(
            not_valid_after
        ).sign(key, hashes.SHA256(), default_backend())

    @staticmethod
    def get_pub_key_signature(key, sig):
        return key.sign(
            bytes.fromhex(sig),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )

    @classmethod
    def get_crt_export_bin_sig_rem_sig(cls, cert, key, client):
        crt_export = cert.public_bytes(serialization.Encoding.PEM)
        crt_bin = cert.public_bytes(serialization.Encoding.DER)
        pub_key = cert.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
        crt_hash = hash512(crt_bin.hex())
        rem_sig = client.sign_text(crt_hash)
        crt_sig = cls.get_pub_key_signature(key, rem_sig).hex()

        valid_from = int(cert.not_valid_before.strftime("%s"))
        valid_to = int(cert.not_valid_after.strftime("%s"))

        return crt_export, crt_bin, crt_sig, rem_sig, pub_key, valid_from, valid_to

    def process_csr(self, certificate_request, key, not_valid_before=None, not_valid_after=None):
        public_key = certificate_request.public_key()
        subject = certificate_request.subject
        issuer = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, PUB_KEY_ORGANIZATION),
            x509.NameAttribute(NameOID.USER_ID, self.get_signer_pubkey())
        ])

        not_valid_before = not_valid_before if not_valid_before else datetime.datetime.utcnow()
        not_valid_after = not_valid_after if not_valid_after else not_valid_before + PUB_KEY_MAX_VALIDITY

        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            not_valid_before
        ).not_valid_after(
            not_valid_after
        ).sign(key, hashes.SHA256(), default_backend())

    def store_pub_key(self, public_key, entity_hash, entity_hash_signature, valid_from, valid_to):
        payload = self.get_new_pub_key_payload(public_key,
                                               entity_hash,
                                               entity_hash_signature,
                                               valid_from,
                                               valid_to)

        crt_address = self.make_address_from_data(public_key)
        account_address = AccountHandler().make_address_from_data(self._signer.get_public_key().as_hex())
        settings_address = _make_settings_key('remme.economy_enabled')
        storage_pub_key = _make_settings_key(SETTINGS_STORAGE_PUB_KEY)
        storage_address = AccountHandler().make_address_from_data(storage_pub_key)
        addresses_input = [crt_address, account_address, settings_address, self.get_user_address(), storage_pub_key]
        addresses_output = [crt_address, self.get_user_address(), storage_address]
        return self._send_transaction(PubKeyMethod.STORE, payload, addresses_input, addresses_output), crt_address

    def revoke_pub_key(self, crt_address):
        payload = self.get_revoke_payload(crt_address)
        addresses_input = [crt_address]
        addresses_output = addresses_input
        return self._send_transaction(PubKeyMethod.REVOKE, payload, addresses_input, addresses_output)

    def get_signer_pubkey(self):
        return self._signer.get_public_key().as_hex()

    def sign_text(self, data):
        return self._signer.sign(data.encode('utf-8'))

    async def get_status(self, address):
        data = await self.get_value(address)
        storage = PubKeyStorage()
        storage.ParseFromString(data)
        return storage
