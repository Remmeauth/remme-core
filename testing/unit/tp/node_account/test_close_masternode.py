"""
Provide tests for node account handler close masternode implementation
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


def test_close_masternode():
    """
    Case: close masternode
    Expect: masternode is closed, all reputation tokens are transferred to operational account
    """
    FROZEN = 300000
    UNFROZEN = 10000
    OPERATIONAL = 5000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = 300000

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
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

    mock_context = create_context(account_from_balance=OPERATIONAL, node_state=NodeAccount.NodeState.Value('OPENED'),
                                  frozen=FROZEN, unfrozen=UNFROZEN)

    NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ACCOUNT_ADDRESS_FROM
    ])

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).balance == OPERATIONAL + FROZEN + UNFROZEN
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation.frozen == 0
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation.unfrozen == 0
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).node_state == NodeAccount.NodeState.Value('CLOSED')


def test_close_new_masternode():
    """
    Case: close not opened masternode
    Expect: Exception: Masternode is not opened or has been closed.
    """
    FROZEN = 300000
    UNFROZEN = 10000
    OPERATIONAL = 5000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = 300000

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
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

    mock_context = create_context(account_from_balance=OPERATIONAL, node_state=NodeAccount.NodeState.Value('NEW'),
                                  frozen=FROZEN, unfrozen=UNFROZEN)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is not opened or has been closed.' == str(error.value)


def test_close_closed_masternode():
    """
    Case: close closed masternode
    Expect: Exception: Masternode is not opened or has been closed.
    """
    FROZEN = 300000
    UNFROZEN = 10000
    OPERATIONAL = 5000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = 300000

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
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

    mock_context = create_context(account_from_balance=OPERATIONAL, node_state=NodeAccount.NodeState.Value('CLOSED'),
                                  frozen=FROZEN, unfrozen=UNFROZEN)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is not opened or has been closed.' == str(error.value)
