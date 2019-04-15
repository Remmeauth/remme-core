"""
Provide tests for public key handler store method implementation.
"""
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.setting_pb2 import Setting

from remme.protos.account_pb2 import Account
from remme.protos.consensus_account_pb2 import ConsensusAccount
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    PubKeyMethod,
    NewPubKeyPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import client_to_real_amount
from remme.tp.consensus_account import ConsensusAccountHandler
from remme.tp.pub_key import (
    PUB_KEY_STORE_PRICE,
    PubKeyHandler,
)
from testing.conftest import create_signer
from testing.utils.client import (
    generate_address,
    generate_rsa_signature,
    proto_error_msg,
)
from testing.mocks.stub import StubContext
from .base import (
    ADDRESS_FROM_ECDSA_PUBLIC_KEY,
    ADDRESS_FROM_ED25519_PUBLIC_KEY,
    ADDRESS_FROM_RSA_PUBLIC_KEY,
    SENDER_PUBLIC_KEY,
    SENDER_PRIVATE_KEY,
    SENDER_ADDRESS,
    SENDER_INITIAL_BALANCE,
    RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY,
    EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
    generate_header,
    generate_rsa_payload,
    generate_ed25519_payload,
    generate_ecdsa_payload,
)

RSA_PAYLOAD = generate_rsa_payload()

INPUTS = OUTPUTS = [
    SENDER_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
]


def test_public_key_handler_store_with_empty_proto():
    """
    Case: send transaction request to store certificate public key with empty proto.
    Expect: invalid transaction error.
    """
    new_public_key_payload = NewPubKeyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        NewPubKeyPayload,
        {
            'entity_hash': ['This field is required.'],
            'entity_hash_signature': ['This field is required.'],
            'valid_from': ['This field is required.'],
            'valid_to': ['This field is required.'],
            'configuration': [
                'At least one of RSAConfiguration, ECDSAConfiguration or Ed25519Configuration must be set',
            ],
        }
    ) == str(error.value)


@pytest.mark.parametrize('address_from_public_key, new_public_key_payload', [
    (ADDRESS_FROM_RSA_PUBLIC_KEY, RSA_PAYLOAD),
    (ADDRESS_FROM_ECDSA_PUBLIC_KEY, generate_ecdsa_payload()),
    (ADDRESS_FROM_ED25519_PUBLIC_KEY, generate_ed25519_payload()),
])
def test_public_key_handler_store(address_from_public_key, new_public_key_payload):
    """
    Case: send transaction request to store public key.
    Expect: public key information is stored to blockchain linked to owner address. Owner paid tokens for storing.
    """
    INPUTS.append(address_from_public_key)
    OUTPUTS.append(address_from_public_key)

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    sender_account = Account()
    sender_account.balance = client_to_real_amount(SENDER_INITIAL_BALANCE)
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    consensus_account = ConsensusAccount()
    consensus_account.block_cost = 0
    serialized_consensus_account = consensus_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.balance = client_to_real_amount(SENDER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE)
    expected_sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    expected_sender_account.pub_keys.append(address_from_public_key)
    expected_serialized_sender_account = expected_sender_account.SerializeToString()

    expected_consensus_account = ConsensusAccount()
    expected_consensus_account.block_cost = client_to_real_amount(0 + PUB_KEY_STORE_PRICE)
    expected_serialized_consensus_account = expected_consensus_account.SerializeToString()

    expected_state = {
        SENDER_ADDRESS: expected_serialized_sender_account,
        address_from_public_key: expected_serialized_public_key_storage,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: expected_serialized_consensus_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        SENDER_ADDRESS, address_from_public_key,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_non_existing_sender_account():
    """
    Case: send transaction request, to store certificate public key, from non-existing account.
    Expect: invalid transaction error is raised with not enough transferable balance error message.
    """
    new_public_key_payload = RSA_PAYLOAD

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    consensus_account = ConsensusAccount()
    consensus_account.block_cost = 0
    serialized_consensus_account = consensus_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Not enough transferable balance. Sender\'s current balance: 0.' == str(error.value)


def test_public_key_handler_store_decode_error():
    """
    Case: send transaction request, to store certificate public key, with invalid transaction payload.
    Expect: invalid transaction error is raised with cannot decode transaction payload error message.
    """
    serialized_not_valid_transaction_payload = b'F1120071db7c02f5731d06df194dc95465e9b27'

    transaction_header = generate_header(serialized_not_valid_transaction_payload, INPUTS, OUTPUTS)

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

    new_public_key_payload = RSA_PAYLOAD

    transaction_payload = TransactionPayload()
    transaction_payload.method = account_method_impossible_value
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

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
    new_public_key_payload = RSA_PAYLOAD

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    already_registered_public_key = PubKeyStorage()
    already_registered_public_key.owner = SENDER_PUBLIC_KEY
    already_registered_public_key.payload.CopyFrom(new_public_key_payload)
    already_registered_public_key.is_revoked = False
    serialized_already_registered_public_key = already_registered_public_key.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_RSA_PUBLIC_KEY: serialized_already_registered_public_key,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'This public key is already registered.' == str(error.value)


def test_public_key_handler_store_not_der_public_key_format():
    """
    Case: send transaction request to store certificate public key not in DER format.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_der_format_public_key_to_store = b'h8ybuhtvrofpckejfhgubicojslmkghvbiuokl'

    address_from_public_key_to_store = generate_address('pub_key', not_der_format_public_key_to_store)

    inputs = outputs = [
        address_from_public_key_to_store,
        SENDER_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        IS_NODE_ECONOMY_ENABLED_ADDRESS,
    ]

    new_public_key_payload = generate_rsa_payload(key=not_der_format_public_key_to_store)

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, inputs, outputs)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot deserialize the provided public key. Check if it is in DER format.' == str(error.value)


def test_public_key_handler_store_invalid_signature():
    """
    Case: send transaction request, to store certificate public, when signature is invalid.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_user_certificte_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend(),
    )

    entity_hash_signature = generate_rsa_signature(b'w', not_user_certificte_private_key)

    new_public_key_payload = generate_rsa_payload(entity_hash_signature=entity_hash_signature)

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Invalid signature' == str(error.value)


def test_public_key_handler_store_public_key_exceeded_validity():
    """
    Case: send transaction request to store certificate public key with exceeded validity.
    Expect: invalid transaction error is raised with validity exceeds the maximum value error message.
    """
    new_public_key_payload = generate_rsa_payload(valid_to=int(EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP))

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

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
    new_public_key_payload = RSA_PAYLOAD

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    sender_account = Account()
    sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    serialized_sender_account = sender_account.SerializeToString()

    consensus_account = ConsensusAccount()
    serialized_consensus_account = consensus_account.SerializeToString()

    is_economy_enabled_setting = Setting()
    is_economy_enabled_setting.entries.add(key='remme.economy_enabled', value='false')
    serialized_is_economy_enabled_setting = is_economy_enabled_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        SENDER_ADDRESS: serialized_sender_account,
        IS_NODE_ECONOMY_ENABLED_ADDRESS: serialized_is_economy_enabled_setting,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    expected_sender_account.pub_keys.append(ADDRESS_FROM_RSA_PUBLIC_KEY)
    expected_serialized_sender_account = expected_sender_account.SerializeToString()

    expected_consensus_account = ConsensusAccount()
    expected_serialized_consensus_account = expected_consensus_account.SerializeToString()

    expected_state = {
        SENDER_ADDRESS: expected_serialized_sender_account,
        ADDRESS_FROM_RSA_PUBLIC_KEY: expected_serialized_public_key_storage,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: expected_serialized_consensus_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        SENDER_ADDRESS, ADDRESS_FROM_RSA_PUBLIC_KEY,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict
