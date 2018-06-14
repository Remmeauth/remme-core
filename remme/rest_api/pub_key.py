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
import time
from pathlib import Path
from connexion import NoContent

from remme.clients.pub_key import PubKeyClient
from remme.rest_api.pub_key_api_decorator import (
    pub_key_put_request, http_payload_required, pub_key_address_request,
    pub_key_sign_request, p12_pub_key_address_request, cert_key_address_request
)
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
@cert_key_address_request
def post(pub_key_address):
    return execute_post(pub_key_address)


@http_payload_required
@cert_key_address_request
def delete(pub_key_address):
    return execute_delete(pub_key_address)


@http_payload_required
@pub_key_put_request
def put(cert, key, key_export, name_to_save=None, passphrase=None):
    return execute_put(cert, key, key_export, name_to_save, passphrase)


@pub_key_sign_request
def store(cert_request, not_valid_before, not_valid_after):
    return execute_store(cert_request, not_valid_before, not_valid_after)


@http_payload_required
@pub_key_address_request
def post_pub_key(pub_key_address):
    return execute_post(pub_key_address)


@http_payload_required
@pub_key_address_request
def delete_pub_key(pub_key_address):
    return execute_delete(pub_key_address)


@p12_pub_key_address_request
def delete_p12(pub_key_address):
    return execute_delete(pub_key_address)


@p12_pub_key_address_request
def post_p12(pub_key_address):
    return execute_post(pub_key_address)


@http_payload_required
@pub_key_put_request
def put_p12(cert, key, key_export, name_to_save=None, passphrase=None):
    return execute_put(cert, key, key_export, name_to_save, passphrase)


# endregion

# region Logic
def execute_delete(pub_key_address):
    client = PubKeyClient()
    try:
        pub_key_data = client.get_status(pub_key_address)
        if pub_key_data.revoked:
            return {'error': 'The pub_key was already revoked'}, 409
        return client.revoke_pub_key(pub_key_address)
    except KeyNotFound:
        return NoContent, 404


def execute_post(pub_key_address):
    client = PubKeyClient()
    try:
        pub_key_data = client.get_status(pub_key_address)
        now = time.time()
        valid_from = pub_key_data.payload.valid_from
        valid_to = pub_key_data.payload.valid_to
        return {'revoked': pub_key_data.revoked,
                'owner_pub_key': pub_key_data.owner,
                'valid': not pub_key_data.revoked and valid_from < now and now < valid_to,
                'valid_from': valid_from,
                'valid_to': valid_to}
    except KeyNotFound:
        return NoContent, 404


def get_crt_export_bin_sig_rem_sig(cert, key, client):
    crt_export = cert.public_bytes(serialization.Encoding.PEM)
    crt_bin = cert.public_bytes(serialization.Encoding.DER)
    pub_key = cert.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    crt_hash = hash512(crt_bin.hex())
    rem_sig = client.sign_text(crt_hash)
    crt_sig = get_pub_key_signature(key, rem_sig).hex()

    valid_from = int(cert.not_valid_before.timestamp())
    valid_to = int(cert.not_valid_after.timestamp())

    return crt_export, crt_bin, crt_sig, rem_sig, pub_key, valid_from, valid_to


def execute_put(cert, key, key_export, name_to_save=None, passphrase=None):
    client = PubKeyClient()
    crt_export, crt_bin, crt_sig, rem_sig, pub_key, \
        valid_from, valid_to = get_crt_export_bin_sig_rem_sig(cert, key, client)

    try:
        saved_to = save_p12(cert, key, name_to_save, passphrase)
    except ValueError:
        return {'error': 'The file already exists in specified location'}, 409

    batch_id, _ = client.store_pub_key(pub_key, rem_sig, crt_sig, valid_from, valid_to)

    response = {'priv_key': key_export.decode('utf-8'),
                'pub_key': pub_key,
                'crt_key': crt_export.decode('utf-8'),
                'batch_id': batch_id['batch_id']}
    if saved_to:
        response['saved_to'] = saved_to

    return response


def execute_store(cert_request, not_valid_before, not_valid_after):
    pub_key_client = PubKeyClient()

    key = get_keys_to_sign()
    cert = pub_key_client.process_csr(cert_request, key, not_valid_before, not_valid_after)

    crt_export, crt_bin, crt_sig, rem_sig, pub_key, \
        valid_from, valid_to = get_crt_export_bin_sig_rem_sig(cert, key, pub_key_client)

    batch_id, _ = pub_key_client.store_pub_key(pub_key, rem_sig, crt_sig, valid_from, valid_to)

    response = {'pub_key': pub_key,
                'crt_key': crt_export.decode('utf-8'),
                'batch_id': batch_id['batch_id']}

    return response


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


def get_pub_key_signature(key, sig):
    return key.sign(
        bytes.fromhex(sig),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA512()
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
