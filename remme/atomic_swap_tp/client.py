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

import json
import datetime

from remme.protos.certificate_pb2 import NewCertificatePayload, CertificateMethod
from remme.shared.basic_client import BasicClient
from remme.certificate_tp.handler import CertificateHandler


# TODO
class AtomicSwapClient(BasicClient):
    def __init__(self):
        super().__init__(CertificateHandler)

    @classmethod
    def get_payload(self, certificate_raw, signature_rem, signature_crt, cert_signer_public_key):
        payload = NewCertificatePayload()
        payload.certificate_raw = certificate_raw
        payload.signature_rem = signature_rem
        payload.signature_crt = signature_crt
        if cert_signer_public_key:
            payload.cert_signer_public_key = cert_signer_public_key

        return payload

    def revoke_certificate(self, crt_address):
        payload = self.get_revoke_payload(crt_address)
        self._send_transaction(CertificateMethod.REVOKE, payload, [crt_address])

