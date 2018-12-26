import datetime
import time

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

from remme.tp.pub_key import (
    PUB_KEY_MAX_VALIDITY,
    PubKeyHandler,
)
from remme.shared.utils import hash512
from remme.protos.pub_key_pb2 import (
    NewPubKeyPayload,
)
from remme.settings.helper import _make_settings_key
from testing.utils.client import (
    generate_address,
    generate_entity_hash,
    generate_message,
    generate_rsa_signature,
    generate_ed25519_signature,
    generate_ecdsa_signature,
    generate_settings_address,
    generate_rsa_keys,
    generate_ed25519_keys,
    generate_ecdsa_keys,
)


NOT_SENDER_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db1337'

SENDER_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
SENDER_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'
SENDER_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'
SENDER_INITIAL_BALANCE = 5000

CERTIFICATE_PRIVATE_KEY, CERTIFICATE_PUBLIC_KEY = generate_rsa_keys()
ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY = generate_address('pub_key', CERTIFICATE_PUBLIC_KEY)

ED25519_PRIVATE_KEY, ED25519_PUBLIC_KEY = generate_ed25519_keys()
ADDRESS_FROM_ED25519_PUBLIC_KEY = generate_address('pub_key', ED25519_PUBLIC_KEY)

ECDSA_PRIVATE_KEY, ECDSA_PUBLIC_KEY = generate_ecdsa_keys()
ADDRESS_FROM_ECDSA_PUBLIC_KEY = generate_address('pub_key', ECDSA_PUBLIC_KEY)

STORAGE_PUBLIC_KEY = generate_settings_address('remme.settings.storage_pub_key')
STORAGE_ADDRESS = generate_address('account', STORAGE_PUBLIC_KEY)
STORAGE_SETTING_ADDRESS = _make_settings_key('remme.settings.storage_pub_key')

IS_NODE_ECONOMY_ENABLED_ADDRESS = generate_settings_address('remme.economy_enabled')

RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY = 'a23be17ca9c3bd150627ac6469f11ccf25c0c96d8bb8ac333879d3ea06a90413cd4536'
RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

MESSAGE = generate_message('some-data-to-sign')

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

CURRENT_TIMESTAMP = datetime.datetime.now().timestamp()
CURRENT_TIMESTAMP_PLUS_YEAR = CURRENT_TIMESTAMP + PUB_KEY_MAX_VALIDITY.total_seconds()
EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP = CURRENT_TIMESTAMP_PLUS_YEAR + 1

RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE = PERSONAL_PUBLIC_KEY_TYPE_VALUE = 0

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': PubKeyHandler().family_name,
    'family_version': PubKeyHandler()._family_versions[0],
}


def generate_rsa_payload(key=None, entity_hash=None, entity_hash_signature=None, valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR)):
    if key is None:
        key = CERTIFICATE_PUBLIC_KEY
    if entity_hash is None:
        entity_hash = generate_entity_hash(MESSAGE)
    if entity_hash_signature is None:
        entity_hash_signature = generate_rsa_signature(entity_hash, CERTIFICATE_PRIVATE_KEY)
    return NewPubKeyPayload(
        entity_hash=entity_hash,
        entity_hash_signature=entity_hash_signature,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=valid_to,
        rsa=NewPubKeyPayload.RSAConfiguration(
            padding=NewPubKeyPayload.RSAConfiguration.Padding.Value('PKCS1v15'),
            key=key,
        ),
        hashing_algorithm=NewPubKeyPayload.HashingAlgorithm.Value('SHA512')
    )


def generate_ed25519_payload(key=None, entity_hash=None, entity_hash_signature=None, valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR)):
    if key is None:
        key = ED25519_PUBLIC_KEY
    if entity_hash is None:
        entity_hash = generate_entity_hash(MESSAGE)
    if entity_hash_signature is None:
        entity_hash_signature = generate_ed25519_signature(entity_hash, ED25519_PRIVATE_KEY)

    return NewPubKeyPayload(
        entity_hash=entity_hash,
        entity_hash_signature=entity_hash_signature,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=valid_to,
        ed25519=NewPubKeyPayload.Ed25519Configuration(
            key=key,
        ),
        hashing_algorithm=NewPubKeyPayload.HashingAlgorithm.Value('SHA512')
    )


def generate_ecdsa_payload(key=None, entity_hash=None, entity_hash_signature=None, valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR)):
    if key is None:
        key = ECDSA_PUBLIC_KEY
    if entity_hash is None:
        entity_hash = generate_entity_hash(MESSAGE)
    if entity_hash_signature is None:
        entity_hash_signature = generate_ecdsa_signature(entity_hash, ECDSA_PRIVATE_KEY)

    return NewPubKeyPayload(
        entity_hash=entity_hash,
        entity_hash_signature=entity_hash_signature,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=valid_to,
        ecdsa=NewPubKeyPayload.ECDSAConfiguration(
            key=key,
            ec=NewPubKeyPayload.ECDSAConfiguration.EC.Value('SECP256k1'),
        ),
        hashing_algorithm=NewPubKeyPayload.HashingAlgorithm.Value('SHA256')
    )


def generate_header(payload, inputs, outputs):
    return TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=inputs,
        outputs=outputs,
        dependencies=[],
        payload_sha512=hash512(data=payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )
