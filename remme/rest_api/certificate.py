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
import datetime
import hashlib
from connexion import NoContent
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from remme.certificate.certificate_client import CertificateClient
from remme.shared.exceptions import KeyNotFound


def _make_address_from_pem(client, certificate_pem):
    certificate = x509.load_pem_x509_certificate(certificate_pem.encode('utf-8'),
                                                 default_backend())
    crt_bin = certificate.public_bytes(serialization.Encoding.DER).hex()
    address = client.make_address_from_data(crt_bin)
    return address


def post(payload):
    client = CertificateClient()
    address = _make_address_from_pem(client, payload['certificate'])
    try:
        certificate_data = client.get_status(address)
        return {'revoked': certificate_data.revoked,
                'owner': certificate_data.owner}
    except KeyNotFound:
        return NoContent, 404


def delete(payload):
    client = CertificateClient()
    address = _make_address_from_pem(client, payload['certificate'])
    try:
        certificate_data = client.get_status(address)
        if certificate_data.revoked:
            return {'error': 'The certificate was already revoked'}, 500
        client.revoke_certificate(address)
        return {}
    except KeyNotFound:
        return NoContent, 404


def put(payload):
    parameters = {
        'country_name': NameOID.COUNTRY_NAME,
        'state_name': NameOID.STATE_OR_PROVINCE_NAME,
        'locality_name': NameOID.LOCALITY_NAME,
        'common_name': NameOID.COMMON_NAME,
        'name': NameOID.GIVEN_NAME,
        'surname': NameOID.SURNAME,
        'email': NameOID.EMAIL_ADDRESS
    }

    client = CertificateClient()

    encryption_algorithm = serialization.NoEncryption()
    if 'passphrase' in payload.keys():
        if payload['passphrase']:
            encryption_algorithm = serialization.BestAvailableEncryption(
                payload['passphrase'].encode('utf-8'))

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    key_export = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption_algorithm
    )

    name_oid = [x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'REMME'),
                x509.NameAttribute(NameOID.USER_ID, client.get_signer_pubkey())]

    for k, v in parameters.items():
        if k in payload.keys():
            name_oid.append(x509.NameAttribute(v, payload[k]))

    subject = issuer = x509.Name(name_oid)
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=payload['validity'])
    ).sign(key, hashes.SHA256(), default_backend())

    crt_export = cert.public_bytes(serialization.Encoding.PEM)

    crt_bin = cert.public_bytes(serialization.Encoding.DER).hex()
    crt_hash = hashlib.sha512(crt_bin.encode('utf-8')).hexdigest()
    rem_sig = client.sign_text(crt_hash)

    crt_sig = key.sign(
        bytes.fromhex(rem_sig),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    status, _ = client.store_certificate(crt_bin, rem_sig, crt_sig.hex())

    return {'certificate': crt_export.decode('utf-8'),
            'privkey': key_export.decode('utf-8'),
            'batch_id': re.search(r'id=([0-9a-f]+)', status['link']).group(1)}
