"""
Provide tests for node account handler initialize masternode implementation.
"""
import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.node_account_pb2 import (
    NodeAccountInternalTransferPayload,
    NodeAccountMethod,
    NodeAccount,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.utils.client import proto_error_msg

from .shared import (
    RANDOM_NODE_PUBLIC_KEY,
    MINIMUM_STAKE,
    NODE_ACCOUNT_ADDRESS_FROM,
    NODE_ACCOUNT_FROM_PRIVATE_KEY,
    INPUTS,
    OUTPUTS,
    TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
    create_context
)


def test_init_masternode():
    """
    Case: initialize masternode.
    Expect: masternode is initialized.
    """
    initial_stake = 300000
    operational = 10000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = initial_stake - operational

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake)

    NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        NODE_ACCOUNT_ADDRESS_FROM
    ])

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    node_account = state_as_dict.get(NODE_ACCOUNT_ADDRESS_FROM, NodeAccount())

    assert node_account.balance == operational
    assert node_account.reputation.frozen == MINIMUM_STAKE
    assert node_account.reputation.unfrozen == initial_stake - MINIMUM_STAKE - operational
    assert node_account.node_state == NodeAccount.OPENED


def test_low_stake():
    """
    Case: initialize masternode with low stake.
    Expect: invalid transaction exception is raised with initial stake is too low error message.
    """
    initial_stake = MINIMUM_STAKE - 1
    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = initial_stake

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Initial stake is too low.' == str(error.value)


def test_open_masternode_with_invalid_amount():
    """
    Case: initialize masternode with low stake.
    Expect: invalid transaction exception is raised with insufficient tokens on operational account error message.
    """
    initial_stake = MINIMUM_STAKE
    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = initial_stake + 1

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Insufficient amount of tokens on operational account.' == str(error.value)


def test_open_opened_masternode():
    """
    Case: initialize already opened masternode.
    Expect: invalid transaction exception is raised with masternode is already opened or closed error message.
    """
    initial_stake = 300000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = initial_stake

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake, node_state=NodeAccount.OPENED)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is already opened or closed.' == str(error.value)


def test_open_closed_masternode():
    """
    Case: initialize already closed masternode.
    Expect: invalid transaction exception is raised with masternode is already opened or closed error message.
    """
    initial_stake = 300000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = initial_stake

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake, node_state=NodeAccount.CLOSED)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is already opened or closed.' == str(error.value)


def test_init_masternode_with_empty_proto():
    """
    Case: initialize masternode with empty proto.
    Expect: invalid transaction exception is raised with could not transfer with zero amount error message.
    """
    initial_stake = MINIMUM_STAKE - 1
    internal_transfer_payload = NodeAccountInternalTransferPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.INITIALIZE_MASTERNODE
    transaction_payload.data = internal_transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=initial_stake)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        NodeAccountInternalTransferPayload,
        {
            'value': ['Could not transfer with zero amount.'],
        }
    ) == str(error.value)
