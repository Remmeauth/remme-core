"""
Provide tests for node account handler apply (genesis) method implementation.
"""
import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.account_pb2 import (
    Account,
    AccountMethod,
    TransferPayload,
)
from remme.protos.node_account_pb2 import NodeAccountInternalTransferPayload, NodeAccountMethod, NodeAccount
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import ZERO_ADDRESS
from remme.shared.utils import hash512
from remme.tp.account import AccountHandler
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

from .shared import *

def test_init_masternode():
    """
    Case: initialize masternode
    Expect: masternode is initialized
    """
    INITIAL_STAKE = 300000
    OPERATIONAL = 10000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = INITIAL_STAKE - OPERATIONAL

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
        signature=create_signer(private_key=ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=INITIAL_STAKE)

    NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ACCOUNT_ADDRESS_FROM
    ])

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).balance == OPERATIONAL
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation.frozen == MINIMUM_STAKE
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation.unfrozen == INITIAL_STAKE - MINIMUM_STAKE - OPERATIONAL
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).node_state == NodeAccount.NodeState.Value('OPENED')


def test_low_stake():
    """
    Case: initialize masternode
    Expect: masternode is initialized
    """
    INITIAL_STAKE = MINIMUM_STAKE - 1
    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = INITIAL_STAKE

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
        signature=create_signer(private_key=ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=INITIAL_STAKE)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Initial stake is too low' == str(error.value)


def test_open_opened_masternode():
    """
    Case: initialize masternode
    Expect: masternode is initialized
    """
    INITIAL_STAKE = 300000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = INITIAL_STAKE

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
        signature=create_signer(private_key=ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=INITIAL_STAKE, node_state=NodeAccount.NodeState.Value('OPENED'))

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is already opened or closed' == str(error.value)


def test_open_closed_masternode():
    """
    Case: initialize masternode
    Expect: masternode is initialized
    """
    INITIAL_STAKE = 300000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = INITIAL_STAKE

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
        signature=create_signer(private_key=ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=INITIAL_STAKE, node_state=NodeAccount.NodeState.Value('CLOSED'))

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is already opened or closed' == str(error.value)
