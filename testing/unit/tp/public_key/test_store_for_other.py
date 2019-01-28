"""
Provide tests for public key handler store method implementation.
"""
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.setting_pb2 import Setting
from sawtooth_signing.secp256k1 import (
    Secp256k1PrivateKey,
    Secp256k1Context
)

from remme.protos.account_pb2 import Account
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    PubKeyMethod,
    NewPubKeyPayload,
    NewPubKeyStoreAndPayPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import ZERO_ADDRESS
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
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    CERTIFICATE_PUBLIC_KEY,
    ED25519_PUBLIC_KEY,
    ADDRESS_FROM_ED25519_PUBLIC_KEY,
    ECDSA_PUBLIC_KEY,
    ADDRESS_FROM_ECDSA_PUBLIC_KEY,
    EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
    generate_header,
    generate_rsa_payload,
    generate_ed25519_payload,
    generate_ecdsa_payload,
)

OWNER_PRIVATE_KEY = 'baea35704ff361475ede4f6fee4a542e2e74eaaf07c38e1d1931e07de5e6487f'
OWNER_PUBLIC_KEY = '022a20772a806cf32393663055ae8ad26e60ee2619ae449fe7b6ebe0f355006c4e'
OWNER_ADDRESS = '11200781ae7b6618d6eae1fba104f3ed5565fab462a6f735b3e2a3978d5d5c1fe81579'

PAYER_PRIVATE_KEY = 'bdf1567f8f3374d128d32466eb9862ecb0f2f23930abd6ee94990f418780e889'
PAYER_PUBLIC_KEY = '0360f28da594661d39deabf2817cad2bdacdcca043e91004d3c935fa9e93caa1a3'
PAYER_ADDRESS = '1120078c9ac38f8b9c6c0560afd71ade8b7821cc5a43486320578f9fa8414ee975af88'
PAYER_INITIAL_BALANCE = 5000

RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS = 'a23be17ca9c3bd150627ac6469f11ccf25c0c96d8bb8ac333879d3ea06a90413cd4536'

INPUTS = OUTPUTS = [
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    OWNER_ADDRESS,
    PAYER_ADDRESS,
    ZERO_ADDRESS,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
]


# def test_store_rsa_public_key_for_other_with_empty_proto():
#     """
#     Case: send transaction request to store certificate public key with empty protobuf.
#     Expect: invalid transaction error with detailed description about missed protobuf parameters.
#     """
#     new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload()
#
#     transaction_payload = TransactionPayload()
#     transaction_payload.method = PubKeyMethod.STORE_AND_PAY
#     transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()
#
#     serialized_transaction_payload = transaction_payload.SerializeToString()
#
#     transaction_header = generate_header(
#         serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
#     )
#
#     serialized_header = transaction_header.SerializeToString()
#
#     transaction_request = TpProcessRequest(
#         header=transaction_header,
#         payload=serialized_transaction_payload,
#         signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
#     )
#
#     mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})
#
#     with pytest.raises(InvalidTransaction) as error:
#         PubKeyHandler().apply(transaction=transaction_request, context=mock_context)
#
#     assert proto_error_msg(
#         NewPubKeyStoreAndPayPayload,
#         {
#             'pub_key_payload': {
#                 'hashing_algorithm': ['Not a valid choice'],
#                 'entity_hash': ['This field is required.'],
#                 'entity_hash_signature': ['This field is required.'],
#                 'valid_from': ['This field is required.'],
#                 'valid_to': ['This field is required.'],
#                 'configuration': [
#                     'At least one of RSAConfiguration, ECDSAConfiguration or Ed25519Configuration must be set',
#                 ],
#             },
#             'owner_public_key': ['This field is required.'],
#             'signature_by_owner': ['This field is required.'],
#         }
#     ) == str(error.value)


def test_store_rsa_public_key_for_other():
    """
    Case: send transaction request to store certificate public key (RSA) for other.
    Expect: public key information is stored to blockchain linked to owner address. Transaction sender paid for storing.
    """
    new_public_key_payload = generate_rsa_payload(key=CERTIFICATE_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    payer_account = Account()
    payer_account.balance = PAYER_INITIAL_BALANCE
    serialized_payer_account = payer_account.SerializeToString()

    owner_account = Account()
    owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    serialized_owner_account = owner_account.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        OWNER_ADDRESS: serialized_owner_account,
        PAYER_ADDRESS: serialized_payer_account,
        ZERO_ADDRESS: serialized_zero_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = OWNER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_payer_account = Account()
    expected_payer_account.balance = PAYER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE
    serialized_expected_payer_account = expected_payer_account.SerializeToString()

    expected_owner_account = Account()
    expected_owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    expected_owner_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
    serialized_expected_owner_account = expected_owner_account.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = 0 + PUB_KEY_STORE_PRICE
    expected_serialized_zero_account = expected_zero_account.SerializeToString()

    expected_state = {
        OWNER_ADDRESS: serialized_expected_owner_account,
        PAYER_ADDRESS: serialized_expected_payer_account,
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: expected_serialized_public_key_storage,
        ZERO_ADDRESS: expected_serialized_zero_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        OWNER_ADDRESS, PAYER_ADDRESS, ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY, ZERO_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_store_ed25519_public_key():
    """
    Case: send transaction request to store certificate public key (Ed25519) for other.
    Expect: public key information is stored to blockchain linked to owner address. Transaction sender paid for storing.
    """
    inputs = outputs = [
        ADDRESS_FROM_ED25519_PUBLIC_KEY,
        OWNER_ADDRESS,
        PAYER_ADDRESS,
        ZERO_ADDRESS,
        IS_NODE_ECONOMY_ENABLED_ADDRESS,
    ]

    new_public_key_payload = generate_ed25519_payload(key=ED25519_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    payer_account = Account()
    payer_account.balance = PAYER_INITIAL_BALANCE
    serialized_payer_account = payer_account.SerializeToString()

    owner_account = Account()
    owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    serialized_owner_account = owner_account.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        OWNER_ADDRESS: serialized_owner_account,
        PAYER_ADDRESS: serialized_payer_account,
        ZERO_ADDRESS: serialized_zero_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = OWNER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_payer_account = Account()
    expected_payer_account.balance = PAYER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE
    serialized_expected_payer_account = expected_payer_account.SerializeToString()

    expected_owner_account = Account()
    expected_owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    expected_owner_account.pub_keys.append(ADDRESS_FROM_ED25519_PUBLIC_KEY)
    serialized_expected_owner_account = expected_owner_account.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = 0 + PUB_KEY_STORE_PRICE
    expected_serialized_zero_account = expected_zero_account.SerializeToString()

    expected_state = {
        OWNER_ADDRESS: serialized_expected_owner_account,
        PAYER_ADDRESS: serialized_expected_payer_account,
        ADDRESS_FROM_ED25519_PUBLIC_KEY: expected_serialized_public_key_storage,
        ZERO_ADDRESS: expected_serialized_zero_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        OWNER_ADDRESS, PAYER_ADDRESS, ADDRESS_FROM_ED25519_PUBLIC_KEY, ZERO_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_store_ecdsa_public_key():
    """
    Case: send transaction request to store certificate public key (ECDSA) for other.
    Expect: public key information is stored to blockchain linked to owner address. Transaction sender paid for storing.
    """
    inputs = outputs = [
        ADDRESS_FROM_ECDSA_PUBLIC_KEY,
        OWNER_ADDRESS,
        PAYER_ADDRESS,
        ZERO_ADDRESS,
        IS_NODE_ECONOMY_ENABLED_ADDRESS,
    ]

    new_public_key_payload = generate_ecdsa_payload(key=ECDSA_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    payer_account = Account()
    payer_account.balance = PAYER_INITIAL_BALANCE
    serialized_payer_account = payer_account.SerializeToString()

    owner_account = Account()
    owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    serialized_owner_account = owner_account.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        OWNER_ADDRESS: serialized_owner_account,
        PAYER_ADDRESS: serialized_payer_account,
        ZERO_ADDRESS: serialized_zero_account,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = OWNER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_payer_account = Account()
    expected_payer_account.balance = PAYER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE
    serialized_expected_payer_account = expected_payer_account.SerializeToString()

    expected_owner_account = Account()
    expected_owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    expected_owner_account.pub_keys.append(ADDRESS_FROM_ECDSA_PUBLIC_KEY)
    serialized_expected_owner_account = expected_owner_account.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = 0 + PUB_KEY_STORE_PRICE
    expected_serialized_zero_account = expected_zero_account.SerializeToString()

    expected_state = {
        OWNER_ADDRESS: serialized_expected_owner_account,
        PAYER_ADDRESS: serialized_expected_payer_account,
        ADDRESS_FROM_ECDSA_PUBLIC_KEY: expected_serialized_public_key_storage,
        ZERO_ADDRESS: expected_serialized_zero_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        OWNER_ADDRESS, PAYER_ADDRESS, ADDRESS_FROM_ECDSA_PUBLIC_KEY, ZERO_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_store_public_key_for_other_decode_error():
    """
    Case: send transaction request, to store certificate public key for other, with invalid transaction payload.
    Expect: invalid transaction error is raised with cannot decode transaction payload error message.
    """
    serialized_not_valid_transaction_payload = b'F1120071db7c02f5731d06df194dc95465e9b27'

    transaction_header = generate_header(serialized_not_valid_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_not_valid_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot decode transaction payload.' == str(error.value)


def test_store_public_key_for_other_invalid_transfer_method():
    """
    Case: send transaction request, to store certificate public key for other, with invalid transfer method value.
    Expect: invalid transaction error is raised with invalid account method value error message.
    """
    account_method_impossible_value = 5347

    new_public_key_payload = generate_rsa_payload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = account_method_impossible_value
    transaction_payload.data = new_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Invalid account method value ({account_method_impossible_value}) has been set.' == str(error.value)


def test_store_public_key_for_other_bad_owner_signature():
    """
    Case: send transaction request to store certificate public key for other with bad owner signature.
    Expect: invalid transaction error is raised with public key owner's signature is invalid error message.
    """
    new_public_key_payload = generate_rsa_payload(key=CERTIFICATE_PUBLIC_KEY)

    bad_owner_signature = 'dd8b2dca17d4d507f77edd8b2dca17d4d507f77edd8b2dca17d4d507f77edd8b2dca17d4d507f77e'

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(bad_owner_signature),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    already_registered_public_key = PubKeyStorage()
    already_registered_public_key.owner = OWNER_PUBLIC_KEY
    already_registered_public_key.payload.CopyFrom(new_public_key_payload)
    already_registered_public_key.is_revoked = False
    serialized_already_registered_public_key = already_registered_public_key.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_already_registered_public_key,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Public key owner\'s signature is invalid.' == str(error.value)


def test_store_public_key_for_other_already_registered_public_key():
    """
    Case: send transaction request to store already registered certificate public key for other.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    new_public_key_payload = generate_rsa_payload(key=CERTIFICATE_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    already_registered_public_key = PubKeyStorage()
    already_registered_public_key.owner = OWNER_PUBLIC_KEY
    already_registered_public_key.payload.CopyFrom(new_public_key_payload)
    already_registered_public_key.is_revoked = False
    serialized_already_registered_public_key = already_registered_public_key.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: serialized_already_registered_public_key,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'This public key is already registered.' == str(error.value)


def test_store_public_key_for_other_not_der_public_key_format():
    """
    Case: send transaction request to store certificate public key not in DER format for other.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_der_format_public_key_to_store = b'h8ybuhtvrofpckejfhgubicojslmkghvbiuokl'

    address_from_public_key_to_store = generate_address('pub_key', not_der_format_public_key_to_store)

    inputs = outputs = [
        address_from_public_key_to_store,
        OWNER_ADDRESS,
        ZERO_ADDRESS,
        IS_NODE_ECONOMY_ENABLED_ADDRESS,
    ]

    new_public_key_payload = generate_rsa_payload(key=not_der_format_public_key_to_store)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, inputs, outputs, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot deserialize the provided public key. Check if it is in DER format.' == str(error.value)


def test_store_public_key_for_other_invalid_certificate_signature():
    """
    Case: send transaction request, to store certificate public for other, when certificate signature_by_owner is invalid.
    Expect: invalid transaction error is raised with public key is already registered error message.
    """
    not_user_certificate_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend(),
    )

    entity_hash_signature = generate_rsa_signature(b'w', not_user_certificate_private_key)

    new_public_key_payload = generate_rsa_payload(
        key=CERTIFICATE_PUBLIC_KEY, entity_hash_signature=entity_hash_signature,
    )
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()
    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)
    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Payed public key has invalid signature.' == str(error.value)


def test_store_public_key_for_other_public_key_exceeded_validity():
    """
    Case: send transaction request to store certificate public key with exceeded validity for other.
    Expect: invalid transaction error is raised with validity exceeds the maximum value error message.
    """
    new_public_key_payload = generate_rsa_payload(
        key=CERTIFICATE_PUBLIC_KEY, valid_to=int(EXCEEDED_PUBLIC_KEY_VALIDITY_TIMESTAMP),
    )
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'The public key validity exceeds the maximum value.' == str(error.value)


def test_store_public_key_for_other_economy_is_not_enabled():
    """
    Case: send transaction request, to store certificate public key for other, when economy isn't enabled.
    Expect: public key information is stored to blockchain linked to owner address. Owner hasn't paid for storing.
    """
    new_public_key_payload = generate_rsa_payload(key=CERTIFICATE_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature_by_owner = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=bytes.fromhex(OWNER_PUBLIC_KEY),
        signature_by_owner=bytes.fromhex(signature_by_owner),
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.STORE_AND_PAY
    transaction_payload.data = new_public_key_store_and_pay_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(
        serialized_transaction_payload, INPUTS, OUTPUTS, signer_public_key=PAYER_PUBLIC_KEY,
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=PAYER_PRIVATE_KEY).sign(serialized_header),
    )

    payer_account = Account()
    payer_account.balance = PAYER_INITIAL_BALANCE
    serialized_payer_account = payer_account.SerializeToString()

    owner_account = Account()
    owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    serialized_owner_account = owner_account.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    is_economy_enabled_setting = Setting()
    is_economy_enabled_setting.entries.add(key='remme.economy_enabled', value='false')
    serialized_is_economy_enabled_setting = is_economy_enabled_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        OWNER_ADDRESS: serialized_owner_account,
        PAYER_ADDRESS: serialized_payer_account,
        ZERO_ADDRESS: serialized_zero_account,
        IS_NODE_ECONOMY_ENABLED_ADDRESS: serialized_is_economy_enabled_setting,
    })

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = OWNER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_payer_account = Account()
    expected_payer_account.balance = PAYER_INITIAL_BALANCE
    serialized_expected_payer_account = expected_payer_account.SerializeToString()

    expected_owner_account = Account()
    expected_owner_account.pub_keys.append(RANDOM_ALREADY_STORED_OWNER_PUBLIC_KEY_ADDRESS)
    expected_owner_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
    serialized_expected_owner_account = expected_owner_account.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = 0
    expected_serialized_zero_account = expected_zero_account.SerializeToString()

    expected_state = {
        OWNER_ADDRESS: serialized_expected_owner_account,
        PAYER_ADDRESS: serialized_expected_payer_account,
        ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY: expected_serialized_public_key_storage,
        ZERO_ADDRESS: expected_serialized_zero_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        OWNER_ADDRESS, PAYER_ADDRESS, ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY, ZERO_ADDRESS,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict
