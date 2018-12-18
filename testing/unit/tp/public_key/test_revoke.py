"""
Provide tests for public key handler store method implementation.
"""
import binascii
import datetime
import time

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload,
    RevokePubKeyPayload,
    PubKeyMethod,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.tp.pub_key import (
    PUB_KEY_MAX_VALIDITY,
    PubKeyHandler,
)
from testing.conftest import create_signer
from testing.utils.client import (
    generate_address,
    generate_entity_hash,
    generate_message,
    generate_signature,
)
from testing.mocks.stub import StubContext

NOT_SENDER_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db1337'

SENDER_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
SENDER_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'

CERTIFICATE_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend(),
)

CERTIFICATE_PUBLIC_KEY = CERTIFICATE_PRIVATE_KEY.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY = generate_address('pub_key', CERTIFICATE_PUBLIC_KEY)

MESSAGE = generate_message('some-data-to-sign')
ENTITY_HASH = generate_entity_hash(MESSAGE)
ENTITY_HASH_SIGNATURE = generate_signature(ENTITY_HASH, CERTIFICATE_PRIVATE_KEY)

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

CURRENT_TIMESTAMP = datetime.datetime.now().timestamp()
CURRENT_TIMESTAMP_PLUS_YEAR = CURRENT_TIMESTAMP + PUB_KEY_MAX_VALIDITY.total_seconds()

RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE = PERSONAL_PUBLIC_KEY_TYPE_VALUE = 0

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': PubKeyHandler().family_name,
    'family_version': PubKeyHandler()._family_versions[0],
}

INPUTS = OUTPUTS = [
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
]


def test_public_key_handler_revoke():
    """
    Case: send transaction request to revoke certificate public key.
    Expect: public key storage blockchain record is changed to True.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.revoked = False
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_existing_public_key_storage,
    })

    expected_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(expected_public_key_payload)
    expected_public_key_storage.revoked = True
    serialized_expected_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_state = {
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_expected_public_key_storage,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_revoke_non_existent_public_key():
    """
    Case: send transaction request to revoke non-existent certificate public key.
    Expect: invalid transaction error is raised with no certificate public key is presented in chain error message.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'No public key is presented in chain.' == str(error.value)


def test_public_key_handler_revoke_not_owner_public_key():
    """
    Case: send transaction request to revoke another ownder certificate public key.
    Expect: invalid transaction error is raised with no certificate public key is presented in chain error message.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = NOT_SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.revoked = False
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_existing_public_key_storage,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Only owner can revoke the public key.' == str(error.value)


def test_public_key_handler_revoke_already_revoked():
    """
    Case: send transaction request to revoke already revoked certificate public key.
    Expect: invalid transaction error is raised with no certificate public key is presented in chain error message.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.revoked = True
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_existing_public_key_storage,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'The public key is already revoked.' == str(error.value)
