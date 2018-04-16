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

import re
import hashlib
from connexion import NoContent
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from remme.certificate.certificate_client import CertificateClient
from remme.rest_api.certificate_api_decorator import certificate_put_request,\
    http_payload_required, certificate_address_request
from remme.shared.exceptions import KeyNotFound


@http_payload_required
@certificate_address_request
def post(certificate_address):
    client = CertificateClient()
    try:
        certificate_data = client.get_status(certificate_address)
        return {'revoked': certificate_data.revoked,
                'owner': certificate_data.owner}
    except KeyNotFound:
        return NoContent, 404


@http_payload_required
@certificate_address_request
def delete(certificate_address):
    client = CertificateClient()
    try:
        certificate_data = client.get_status(certificate_address)
        if certificate_data.revoked:
            return {'error': 'The certificate was already revoked'}, 409
        client.revoke_certificate(certificate_address)
        return NoContent, 204
    except KeyNotFound:
        return NoContent, 404


@http_payload_required
@certificate_put_request
def put(cert, key, key_export):
    certificate_client = CertificateClient()

    crt_export = cert.public_bytes(serialization.Encoding.PEM)
    crt_bin = cert.public_bytes(serialization.Encoding.DER).hex()
    crt_hash = hashlib.sha512(crt_bin.encode('utf-8')).hexdigest()
    rem_sig = certificate_client.sign_text(crt_hash)
    crt_sig = key.sign(
        bytes.fromhex(rem_sig),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    status, _ = certificate_client.store_certificate(crt_bin, rem_sig, crt_sig.hex())

    return {'certificate': crt_export.decode('utf-8'),
            'priv_key': key_export.decode('utf-8'),
            'batch_id': re.search(r'id=([0-9a-f]+)', status['link']).group(1)}
