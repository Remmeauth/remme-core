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

from remme.protos.certificate_pb2 import CertificateStorage, \
    NewCertificatePayload, RevokeCertificatePayload, CertificateMethod
from remme.shared.basic_client import BasicClient
from remme.certificate.certificate_handler import CertificateHandler


class CertificateClient(BasicClient):
    def __init__(self):
        super().__init__(CertificateHandler)

    @classmethod
    def get_new_certificate_payload(self, certificate_raw, signature_rem, signature_crt):
        payload = NewCertificatePayload()
        payload.certificate_raw = certificate_raw
        payload.signature_rem = signature_rem
        payload.signature_crt = signature_crt

        return payload

    @classmethod
    def get_revoke_payload(self, crt_address):
        payload = RevokeCertificatePayload()
        payload.address = crt_address

        return payload

    def store_certificate(self, certificate_raw, signature_rem, signature_crt):
        payload = self.get_new_certificate_payload(certificate_raw, signature_rem, signature_crt)
        crt_address = self.make_address_from_data(certificate_raw)
        print('Certificate address', crt_address)
        self._send_transaction(CertificateMethod.STORE, payload, [crt_address])

    def revoke_certificate(self, crt_address):
        payload = self.get_revoke_payload(crt_address)
        self._send_transaction(CertificateMethod.REVOKE, payload, [crt_address])

    def get_signer_pubkey(self):
        return self._signer.get_public_key().as_hex()

    def sign_text(self, data):
        return self._signer.sign(data.encode('utf-8'))

    def get_status(self, address):
        data = self.get_value(address)
        storage = CertificateStorage()
        storage.ParseFromString(data)
        return storage.revoked
