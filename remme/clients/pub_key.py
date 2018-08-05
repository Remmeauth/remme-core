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

from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload, RevokePubKeyPayload, PubKeyMethod
)
from remme.clients.basic import BasicClient
from remme.tp.pub_key import PubKeyHandler
from remme.tp.account import AccountHandler
from remme.tp.pub_key import PUB_KEY_ORGANIZATION, PUB_KEY_MAX_VALIDITY
from remme.settings.helper import _make_settings_key

from cryptography.x509.oid import NameOID
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class PubKeyClient(BasicClient):
    def __init__(self, test_helper=None):
        super().__init__(PubKeyHandler, test_helper=test_helper)

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
        account_address = AccountHandler.make_address_from_data(self._signer.get_public_key().as_hex())
        settings_address = _make_settings_key('remme.economy_enabled')
        return self._send_transaction(PubKeyMethod.STORE, payload, [crt_address, account_address, settings_address]), crt_address

    def revoke_pub_key(self, crt_address):
        payload = self.get_revoke_payload(crt_address)
        return self._send_transaction(PubKeyMethod.REVOKE, payload, [crt_address])

    def get_signer_pubkey(self):
        return self._signer.get_public_key().as_hex()

    def sign_text(self, data):
        return self._signer.sign(data.encode('utf-8'))

    def get_status(self, address):
        data = self.get_value(address)
        storage = PubKeyStorage()
        storage.ParseFromString(data)
        return storage
