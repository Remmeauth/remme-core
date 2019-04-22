"""
Provide tests for public key handler store method implementation.
"""
import pytest
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest

from remme.protos.account_pb2 import Account
from remme.protos.pub_key_pb2 import (
    PubKeyStorage,
    RevokePubKeyPayload,
    PubKeyMethod,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import TRANSACTION_FEE
from remme.shared.utils import client_to_real_amount
from remme.tp.pub_key import PubKeyHandler
from remme.tp.consensus_account import ConsensusAccountHandler, ConsensusAccount

from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg
from .base import (
    ADDRESS_FROM_RSA_PUBLIC_KEY,
    SENDER_PUBLIC_KEY,
    SENDER_PRIVATE_KEY,
    SENDER_ADDRESS,
    NOT_SENDER_PUBLIC_KEY,
    generate_header,
    generate_rsa_payload,
)


INPUTS = OUTPUTS = [
    ADDRESS_FROM_RSA_PUBLIC_KEY,
    SENDER_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
]


def test_public_key_handler_revoke_with_empty_proto():
    """
    Case: send transaction request to revoke another ownder certificate public key with empty proto
    Expect: invalid transaction error
    """
    revoke_public_key_payload = RevokePubKeyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

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
        RevokePubKeyPayload,
        {'address': ['Missed address.']}
    ) == str(error.value)


def test_public_key_handler_revoke():
    """
    Case: send transaction request to revoke certificate public key.
    Expect: public key storage blockchain record is changed to True.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_RSA_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = generate_rsa_payload()

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.is_revoked = False
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    consensus_account = ConsensusAccount()
    consensus_account.block_cost = 0
    serialized_consensus_account = consensus_account.SerializeToString()

    sender_account = Account()
    sender_account.balance = client_to_real_amount(TRANSACTION_FEE)
    serialized_sender_account = sender_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_RSA_PUBLIC_KEY: serialized_existing_public_key_storage,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
        SENDER_ADDRESS: serialized_sender_account,
    })

    expected_public_key_payload = generate_rsa_payload()

    expected_public_key_storage = PubKeyStorage()
    expected_public_key_storage.owner = SENDER_PUBLIC_KEY
    expected_public_key_storage.payload.CopyFrom(expected_public_key_payload)
    expected_public_key_storage.is_revoked = True
    serialized_expected_public_key_storage = expected_public_key_storage.SerializeToString()

    expected_consensus_account = ConsensusAccount()
    expected_consensus_account.block_cost = client_to_real_amount(TRANSACTION_FEE)
    serialized_expected_consensus_account = expected_consensus_account.SerializeToString()

    expected_sender_account = Account()
    sender_account.balance = 0
    serialized_expected_sender_account = expected_sender_account.SerializeToString()

    expected_state = {
        ADDRESS_FROM_RSA_PUBLIC_KEY: serialized_expected_public_key_storage,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_expected_consensus_account,
        SENDER_ADDRESS: serialized_expected_sender_account,
    }

    PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ADDRESS_FROM_RSA_PUBLIC_KEY,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        SENDER_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_revoke_non_existent_public_key():
    """
    Case: send transaction request to revoke non-existent certificate public key.
    Expect: invalid transaction error is raised with no certificate public key is presented in chain error message.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_RSA_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

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

    assert 'No public key is presented in chain.' == str(error.value)


def test_public_key_handler_revoke_not_owner_public_key():
    """
    Case: send transaction request to revoke another ownder certificate public key.
    Expect: invalid transaction error is raised with no certificate public key is presented in chain error message.
    """
    revoke_public_key_payload = RevokePubKeyPayload(
        address=ADDRESS_FROM_RSA_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = generate_rsa_payload()

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = NOT_SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.is_revoked = False
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_RSA_PUBLIC_KEY: serialized_existing_public_key_storage,
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
        address=ADDRESS_FROM_RSA_PUBLIC_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = PubKeyMethod.REVOKE
    transaction_payload.data = revoke_public_key_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = generate_header(serialized_transaction_payload, INPUTS, OUTPUTS)

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=SENDER_PRIVATE_KEY).sign(serialized_header),
    )

    existing_public_key_payload = generate_rsa_payload()

    existing_public_key_storage = PubKeyStorage()
    existing_public_key_storage.owner = SENDER_PUBLIC_KEY
    existing_public_key_storage.payload.CopyFrom(existing_public_key_payload)
    existing_public_key_storage.is_revoked = True
    serialized_existing_public_key_storage = existing_public_key_storage.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_FROM_RSA_PUBLIC_KEY: serialized_existing_public_key_storage,
    })

    with pytest.raises(InvalidTransaction) as error:
        PubKeyHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'The public key is already revoked.' == str(error.value)
