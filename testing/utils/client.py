"""
Provide utils clients use to send transaction.

It is vendor code from client library written in Python.

Core also has the same utilities, but it will be easier to substitute these function with
client library function (when it will be uploaded to PyPi), than particularly use core ones.

References:
    - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_utils.py
    - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_public_key_storage.py
"""
import binascii
import hashlib

from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)


def sha256_hexdigest(data):
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def sha512_hexdigest(data):
    return hashlib.sha512(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def generate_address(_family_name, _public_key_to):
    return "" + sha512_hexdigest(_family_name)[:6] + sha512_hexdigest(_public_key_to)[:64]


def generate_signature(data, private_key):
    return binascii.hexlify(private_key.sign(data, padding.PKCS1v15(), hashes.SHA512()))


def generate_message(data):
    return sha512_hexdigest(data)


def generate_entity_hash(message):
    return binascii.unhexlify(message)


def generate_settings_address(key):
    key_parts = key.split(".")[:4]
    address_parts = [sha256_hexdigest(x)[0:16] for x in key_parts]
    while (4 - len(address_parts)) != 0:
        address_parts.append(sha256_hexdigest("")[0:16])
    return "000000" + "".join(address_parts)
