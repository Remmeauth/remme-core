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
from testing.conftest import (
    create_private_key,
    create_signer,
)
from testing.utils.client import (
    generate_rsa_signature, generate_address, proto_error_msg
)
from testing.mocks.stub import StubContext
from .base import (
    CERTIFICATE_PUBLIC_KEY,
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    ADDRESS_FROM_ED25519_PUBLIC_KEY,
    ADDRESS_FROM_ECDSA_PUBLIC_KEY,
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


OWNER_PRIVATE_KEY = 'baea35704ff361475ede4f6fee4a542e2e74eaaf07c38e1d1931e07de5e6487f'
OWNER_PUBLIC_KEY = '022a20772a806cf32393663055ae8ad26e60ee2619ae449fe7b6ebe0f355006c4e'
OWNER_ADDRESS = '11200781ae7b6618d6eae1fba104f3ed5565fab462a6f735b3e2a3978d5d5c1fe81579'

PAYER_PRIVATE_KEY = '8c87d914a6cfeaf027413760ad359b5a56bfe0eda504d879b21872c7dc5b911c'
PAYER_PUBLIC_KEY = '02feb988591c78e58e57cdce5a314bd04798971227fcc2316907355392a2c99c25'
PAYER_ADDRESS = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'
PAYER_INITIAL_BALANCE = 5000

INPUTS = OUTPUTS = [
    ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY,
    OWNER_ADDRESS,
    PAYER_ADDRESS,
    ZERO_ADDRESS,
    IS_NODE_ECONOMY_ENABLED_ADDRESS,
]


def test_public_key_handler_rsa_store():
    """
    Case:
    Expect:
    """
    new_public_key_payload = generate_rsa_payload(key=CERTIFICATE_PUBLIC_KEY)
    serialized_new_public_key_payload = new_public_key_payload.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(OWNER_PRIVATE_KEY)
    signature = Secp256k1Context().sign(serialized_new_public_key_payload, private_key)

    new_public_key_store_and_pay_payload = NewPubKeyStoreAndPayPayload(
        pub_key_payload=new_public_key_payload,
        owner_public_key=OWNER_PUBLIC_KEY.encode(),
        signature_by_owner=signature.encode(),
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
    owner_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
    owner_account.pub_keys.append(ADDRESS_FROM_CERTIFICATE_PUBLIC_KEY)
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
    expected_public_key_storage.owner = OWNER_ADDRESS
    expected_public_key_storage.payload.CopyFrom(new_public_key_payload)
    expected_public_key_storage.is_revoked = False
    expected_serialized_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_payer_account = Account()
    expected_payer_account.balance = PAYER_INITIAL_BALANCE - PUB_KEY_STORE_PRICE
    serialized_expected_payer_account = expected_payer_account.SerializeToString()

    expected_owner_account = Account()
    expected_owner_account.pub_keys.append(RANDOM_ALREADY_STORED_SENDER_PUBLIC_KEY)
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
