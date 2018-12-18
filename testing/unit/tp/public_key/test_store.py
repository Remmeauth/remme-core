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
from sawtooth_sdk.protobuf.setting_pb2 import Setting
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.account_pb2 import Account
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    NewPubKeyPayload,
    PubKeyMethod,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.settings.helper import _make_settings_key
from remme.settings import SETTINGS_STORAGE_PUB_KEY
from remme.tp.pub_key import (
    PUB_KEY_MAX_VALIDITY,
    PUB_KEY_STORE_PRICE,
    PubKeyHandler,
)
from testing.conftest import create_signer
from testing.utils.client import (
    generate_address,
    generate_entity_hash,
    generate_message,
    generate_settings_address,
    generate_signature,
)
from testing.mocks.stub import StubContext

SENDER_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
SENDER_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'
SENDER_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'
SENDER_INITIAL_BALANCE = 5000

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

STORAGE_PUBLIC_KEY = generate_settings_address('remme.settings.storage_pub_key')
STORAGE_ADDRESS = generate_address('account', STORAGE_PUBLIC_KEY)
STORAGE_SETTING_ADDRESS = _make_settings_key('remme.settings.storage_pub_key')

IS_NODE_ECONOMY_ENABLED_ADDRESS = generate_settings_address('remme.economy_enabled')

RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY = 'a23be17ca9c3bd150627ac6469f11ccf25c0c96d8bb8ac333879d3ea06a90413cd4536'
RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

CURRENT_TIMESTAMP = datetime.datetime.now().timestamp()
CURRENT_TIMESTAMP_PLUS_YEAR = CURRENT_TIMESTAMP + PUB_KEY_MAX_VALIDITY.total_seconds()
EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP = CURRENT_TIMESTAMP_PLUS_YEAR + 1

RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE = PERSONAL_PUBLIC_KEY_TYPE_VALUE = 0

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': PubKeyHandler().family_name,
    'family_version': PubKeyHandler()._family_versions[0],
}

INPUTS = OUTPUTS = [
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    SENDER_ADDRESS,
    STORAGE_PUBLIC_KEY,
    STORAGE_ADDRESS,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
]

def test_public_key_handler_store():
    """
    Case: send transaction request to store certificate public key.
    Expect: public key information is stored to blockchain linked to owner address. Owner paid tokens for storing.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    sender_account = Account()
    sender_account.balance = SENDER_INITIAL_BALANCE
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    storage_account = Account()
    storage_account.balance = 0
    serialized_storage_account = storage_account.SerializeToString()

    storage_setting = Setting()
    storage_setting.entries.add(key=SETTINGS_STORAGE_PUB_KEY, value=STORAGE_PUBLIC_KEY)
    serialized_storage_setting = storage_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        STORAGE_SETTING_ADDRESS: serialized_storage_setting,
        STORAGE_ADDRESS: serialized_storage_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.balance = SENDER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE
    expected_sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    expected_sender_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
    expected_serialized_sender_account = expected_sender_account.SerializeToString()

    expected_storage_account = Account()
    expected_storage_account.balance = 0 + PUB_KEY_STORE_PRICE
    expected_serialized_storage_account = expected_storage_account.SerializeToString()

    expected_state = {
        SENDER_ADDRESS: expected_serialized_sender_account,
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: expected_serialized_public_key_storage,
        STORAGE_ADDRESS: expected_serialized_storage_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        SENDER_ADDRESS, ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY, STORAGE_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_store_decode_error():
    """
    Case: send transaction request, to store certificate public key, with invalid transaction payload.
    Expect: invalid transaction error is raised with cannot decode transaction payload error message.
    """
    serialized_not_valid_transaction_payload = b'F1120071db7c02f5731d06df194dc95465e9b27'

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_not_valid_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_not_valid_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot decode transaction payload.' == str(error.value)


def test_public_key_handler_store_invalid_transfer_method():
    """
    Case: send transaction request, to store certificate public key, with invalid transfer method value.
    Expect: invalid transaction error is raised with invalid account method value error message.
    """
    account_method_impossible_value = 5347

    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = account_method_impossible_value
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    assert f'Invalid account method value ({account_method_impossible_value}) has been set.' == str(error.value)


def test_public_key_handler_store_already_registered_public_key():
    """
    Case: send transaction request to store already registered certificate public key.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    already_registered_public_key = PubKeyStorage()
    already_registered_public_key.owner = SENDER_PUBLIC_KEY
    already_registered_public_key.payload.CopyFrom(new_public_key_payload)
    already_registered_public_key.revoked = False
    serialized_already_registered_public_key = already_registered_public_key.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_already_registered_public_key,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'This public key is already registered.' == str(error.value)


def test_public_key_handler_store_not_pem_public_key_format():
    """
    Case: send transaction request to store certificate public key not in PEM format.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_pem_format_public_key_to_store = 'h8ybuhtvrofpckejfhgubicojslmkghvbiuokl'

    address_from_public_key_to_store = generate_address('pub_key', not_pem_format_public_key_to_store)

    inputs = outputs = [
        address_from_public_key_to_store,
        SENDER_ADDRESS,
        STORAGE_PUBLIC_KEY,
        STORAGE_ADDRESS,
        IS_NODE_ECONOMY_ENABLED_ADDRESS,
    ]

    new_public_key_payload = NewPubKeyPayload(
        public_key=not_pem_format_public_key_to_store,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=SENDER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=inputs,
        outputs=outputs,
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

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot deserialize the provided public key. Check if it is in PEM format.' == str(error.value)


def test_public_key_handler_store_entity_has_not_hex_format():
    """
    Case: send transaction request, to store certificate public key, when entity has not hex format.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_used_in_hex_validation_symbols = 'gklprts'

    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=not_used_in_hex_validation_symbols,
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    assert 'Entity hash or/and signature is not a hex format.' == str(error.value)


def test_public_key_handler_store_invalid_signature():
    """
    Case: send transaction request, to store certificate public, when signature is invalid.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_user_certificte_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend(),
    )

    entity_hash_signature = generate_signature(ENTITY_HASH, not_user_certificte_private_key)

    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=entity_hash_signature,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    assert 'Invalid signature.' == str(error.value)


def test_public_key_handler_store_public_key_exceeded_validity():
    """
    Case: send transaction request to store certificate public key with exceeded validity.
    Expect: invalid transaction error is raised with validity exceeds the maximum value error message.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    assert 'The public key validity exceeds the maximum value.' == str(error.value)


def test_public_key_handler_store_economy_is_not_enabled():
    """
    Case: send transaction request, to store certificate public key, when economy isn't enabled.
    Expect: public key information is stored to blockchain linked to owner address. Owner hasn't paid for storing.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    sender_account = Account()
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    storage_account = Account()
    serialized_storage_account = storage_account.SerializeToString()

    storage_setting = Setting()
    storage_setting.entries.add(key=SETTINGS_STORAGE_PUB_KEY, value=STORAGE_PUBLIC_KEY)
    serialized_storage_setting = storage_setting.SerializeToString()

    is_economy_enabled_setting = Setting()
    is_economy_enabled_setting.entries.add(key='remme.economy_enabled', value='false')
    serialized_is_economy_enabled_setting = is_economy_enabled_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        STORAGE_SETTING_ADDRESS: serialized_storage_setting,
        IS_NODE_ECONOMY_ENABLED_ADDRESS: serialized_is_economy_enabled_setting,
        STORAGE_ADDRESS: serialized_storage_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    expected_sender_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
    expected_serialized_sender_account = expected_sender_account.SerializeToString()

    expected_storage_account = Account()
    expected_serialized_storage_account = expected_storage_account.SerializeToString()

    expected_state = {
        SENDER_ADDRESS: expected_serialized_sender_account,
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: expected_serialized_public_key_storage,
        STORAGE_ADDRESS: expected_serialized_storage_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        SENDER_ADDRESS, ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY, STORAGE_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_store_storage_public_key_is_not_set():
    """
    Case: send transaction request, to store certificate public key, when storage public key isn't set.
    Expect: public key information is stored to blockchain linked to owner address. Owner paid tokens for storing.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    sender_account = Account()
    sender_account.balance = SENDER_INITIAL_BALANCE
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    storage_account = Account()
    storage_account.balance = 0
    serialized_storage_account = storage_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        STORAGE_ADDRESS: serialized_storage_account,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'The node\'s storage public key hasn\'t been set, get node config to ensure.' == str(error.value)


def test_public_key_handler_store_sender_is_node():
    """
    Case: send transaction request, to store certificate public key, when sender is node (same addresses).
    Expect: public key information is stored to blockchain linked to owner address. Owner hasn't paid for storing.
    """
    new_public_key_payload = NewPubKeyPayload(
        public_key=CERTIFICATE_PUBLIC_KEY,
        public_key_type=RSA_PUBLIC_KEY_TO_STORE_TYPE_VALUE,
        entity_type=PERSONAL_PUBLIC_KEY_TYPE_VALUE,
        entity_hash=binascii.hexlify(ENTITY_HASH),
        entity_hash_signature=ENTITY_HASH_SIGNATURE,
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

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

    sender_account = Account()
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    storage_account = Account()
    serialized_storage_account = storage_account.SerializeToString()

    storage_setting = Setting()
    storage_setting.entries.add(key=SETTINGS_STORAGE_PUB_KEY, value=SENDER_PUBLIC_KEY)
    serialized_storage_setting = storage_setting.SerializeToString()

    is_economy_enabled_setting = Setting()
    is_economy_enabled_setting.entries.add(key='remme.economy_enabled', value='false')
    serialized_is_economy_enabled_setting = is_economy_enabled_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        STORAGE_SETTING_ADDRESS: serialized_storage_setting,
        IS_NODE_ECONOMY_ENABLED_ADDRESS: serialized_is_economy_enabled_setting,
        STORAGE_ADDRESS: serialized_storage_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    expected_sender_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
    expected_serialized_sender_account = expected_sender_account.SerializeToString()

    expected_storage_account = Account()
    expected_serialized_storage_account = expected_storage_account.SerializeToString()

    expected_state = {
        SENDER_ADDRESS: expected_serialized_sender_account,
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: expected_serialized_public_key_storage,
        STORAGE_ADDRESS: expected_serialized_storage_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        SENDER_ADDRESS, ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY, STORAGE_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict
