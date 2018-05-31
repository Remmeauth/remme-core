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
import os
from pathlib import Path
import re
import hashlib
from connexion import NoContent

from remme.certificate.client import CertificateClient
from remme.rest_api.certificate_api_decorator import certificate_put_request, \
    http_payload_required, certificate_address_request, certificate_sign_request, \
    p12_certificate_address_request
from remme.shared.exceptions import KeyNotFound

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from OpenSSL.crypto import PKCS12, X509, PKey


from remme.shared.utils import hash512

PATH_TO_EXPORTS_FOLDER = Path('/root/usr/share')
HOST_FOLDER_EXPORTS_PATH_ENV_KEY = 'REMME_CONTAINER_EXPORTS_FOLDER'
REMME_CA_KEY_FILE = PATH_TO_EXPORTS_FOLDER.joinpath('REMME_CA_KEY.pem')

LOGGER = logging.getLogger(__name__)

# region Endpoints

@http_payload_required
@certificate_address_request
def post(certificate_address):
    return execute_post(certificate_address)


@http_payload_required
@certificate_address_request
def delete(certificate_address):
    return execute_delete(certificate_address)


@http_payload_required
@certificate_put_request
def put(cert, key, key_export, name_to_save=None, passphrase=None):
    return execute_put(cert, key, key_export, name_to_save, passphrase)


@certificate_sign_request
def store(cert_request, not_valid_before, not_valid_after):
    return execute_store(cert_request, not_valid_before, not_valid_after)


@p12_certificate_address_request
def delete_p12(certificate_address):
    return execute_delete(certificate_address)


@p12_certificate_address_request
def post_p12(certificate_address):
    return execute_post(certificate_address)


@http_payload_required
@certificate_put_request
def put_p12(cert, key, key_export, name_to_save=None, passphrase=None):
    return execute_put(cert, key, key_export, name_to_save, passphrase)


# endregion

# region Logic
def execute_delete(certificate_address):
    client = CertificateClient()
    try:
        certificate_data = client.get_status(certificate_address)
        if certificate_data.revoked:
            return {'error': 'The certificate was already revoked'}, 409
        client.revoke_certificate(certificate_address)
        return NoContent, 200
    except KeyNotFound:
        return NoContent, 404


def execute_post(certificate_address):
    client = CertificateClient()
    try:
        certificate_data = client.get_status(certificate_address)
        return {'revoked': certificate_data.revoked,
                'owner': certificate_data.owner}
    except KeyNotFound:
        return NoContent, 404


def get_crt_export_bin_sig_rem_sig(cert, key):
    certificate_client = CertificateClient()

    crt_export = cert.public_bytes(serialization.Encoding.PEM)
    crt_bin = cert.public_bytes(serialization.Encoding.DER).hex()
    crt_hash = hash512(crt_bin)
    rem_sig = certificate_client.sign_text(crt_hash)
    crt_sig = get_certificate_signature(key, rem_sig)

    return crt_export, crt_bin, crt_sig, rem_sig


def execute_put(cert, key, key_export, name_to_save=None, passphrase=None):
    crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key)

    try:
        saved_to = save_p12(cert, key, name_to_save, passphrase)
    except ValueError:
        return {'error': 'The file already exists in specified location'}, 409

    status, _ = CertificateClient().store_certificate(crt_bin, rem_sig, crt_sig.hex())

    response = {'certificate': crt_export.decode('utf-8'),
                'priv_key': key_export.decode('utf-8'),
                'batch_id': re.search(r'id=([0-9a-f]+)', status['link']).group(1)}
    if saved_to:
        response['saved_to'] = saved_to

    return response


def execute_store(cert_request, not_valid_before, not_valid_after):
    certificate_client = CertificateClient()

    key = get_keys_to_sign()
    cert = certificate_client.process_csr(cert_request, key, not_valid_before, not_valid_after)

    crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key)

    certificate_public_key = key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
    status, _ = certificate_client.store_certificate(crt_bin,
                                                     rem_sig,
                                                     crt_sig.hex(),
                                                     certificate_public_key)

    return {'certificate': crt_export.decode('utf-8'),
            'batch_id': re.search(r'id=([0-9a-f]+)', status['link']).group(1)}


# endregion

# region Helpers

def save_p12(cert, private, file_name, passphrase=None):
    host_folder = os.getenv(HOST_FOLDER_EXPORTS_PATH_ENV_KEY)

    if file_name and host_folder:
        openssl_cert = X509.from_cryptography(cert)
        openssl_priv_key = PKey.from_cryptography_key(private)

        p12 = PKCS12()
        p12.set_privatekey(openssl_priv_key)
        p12.set_certificate(openssl_cert)

        p12bin = p12.export(passphrase)
        file_path = PATH_TO_EXPORTS_FOLDER.joinpath(f'{file_name}.p12')

        if os.path.isfile(file_path):
            raise ValueError
        with file_path.open('wb') as f:
            f.write(p12bin)
        return str(Path(host_folder).joinpath(f'{file_name}.p12'))


def get_certificate_signature(key, rem_sig):
    return key.sign(
        bytes.fromhex(rem_sig),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


# TODO change this method to return node keys (ECDSA)

def save_key(pk, filename):
    LOGGER.info(f'Created key {str(filename)}')
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with filename.open('wb') as pem_out:
        pem_out.write(pem)


def load_key(filename):
    if not os.path.isfile(filename):
        return None
    with filename.open('rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None, default_backend())
    return private_key


def get_keys_to_sign():
    pk = load_key(REMME_CA_KEY_FILE)
    if not pk:
        pk = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend()
        )
        save_key(pk, REMME_CA_KEY_FILE)
    return pk

# endregion