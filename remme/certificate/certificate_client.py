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

import hashlib
from remme.protos.certificate_pb2 import CertificateTransaction, CertificateStorage
from remme.shared.basic_client import BasicClient, _sha512
from remme.certificate.certificate_handler import CertificateHandler


class CertificateClient(BasicClient):
    def __init__(self):
        super().__init__(CertificateHandler)

    def _send_transaction(self, method, data, extra_addresses_input_output):
        addresses_input_output = []
        if extra_addresses_input_output:
            addresses_input_output += extra_addresses_input_output
        return super()._send_transaction(data, addresses_input_output)

    def register_certificate(self, certificate_raw, signature_rem, signature_crt):
        transaction = CertificateTransaction()
        transaction.type = CertificateTransaction.CREATE
        transaction.certificate_raw = certificate_raw
        transaction.signature_rem = signature_rem
        transaction.signature_crt = signature_crt
        crt_address = self.make_address_from_data(certificate_raw)
        print('Certificate address', crt_address)

        self._send_transaction(CertificateTransaction.CREATE, transaction, [crt_address])

    def revoke_certificate(self, address):
        transaction = CertificateTransaction()
        transaction.type = CertificateTransaction.REVOKE
        transaction.address = address
        self._send_transaction(CertificateTransaction.REVOKE, transaction, [address])

    def get_signer_pubkey(self):
        return self._signer.get_public_key().as_hex()

    def sign_text(self, data):
        return self._signer.sign(data.encode('utf-8'))

    def get_status(self, address):
        data = self.get_value(address)
        storage = CertificateStorage()
        storage.ParseFromString(data)
        return storage.revoked
