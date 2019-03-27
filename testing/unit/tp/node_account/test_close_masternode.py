"""
Provide tests for node account handler close masternode implementation.
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
    NodeAccountMethod,
    NodeAccount,
)
from remme.protos.transaction_pb2 import TransactionPayload, EmptyPayload
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer

from .shared import (
    RANDOM_NODE_PUBLIC_KEY,
    NODE_ACCOUNT_ADDRESS_FROM,
    NODE_ACCOUNT_FROM_PRIVATE_KEY,
    INPUTS,
    OUTPUTS,
    TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
    create_context,
)

FROZEN_BALANCE = 300000
UNFROZEN_BALANCE = 10000
OPERATIONAL_BALANCE = 5000


def test_close_masternode():
    """
    Case: close masternode.
    Expect: masternode is closed, all reputation tokens are transferred to operational account.
    """
    close_masternode_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
    transaction_payload.data = close_masternode_payload.SerializeToString()

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

    mock_context = create_context(account_from_balance=OPERATIONAL_BALANCE, node_state=NodeAccount.OPENED,
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE)

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

    assert node_account.balance == OPERATIONAL_BALANCE + FROZEN_BALANCE + UNFROZEN_BALANCE
    assert node_account.reputation.frozen == 0
    assert node_account.reputation.unfrozen == 0
    assert node_account.node_state == NodeAccount.CLOSED


def test_close_new_masternode():
    """
    Case: close not opened masternode.
    Expect: invalid transaction exception is raised with masternode is not opened or has been closed error message.
    """
    close_masternode_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
    transaction_payload.data = close_masternode_payload.SerializeToString()

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

    mock_context = create_context(account_from_balance=OPERATIONAL_BALANCE, node_state=NodeAccount.NEW,
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is not opened or has been closed.' == str(error.value)


def test_close_closed_masternode():
    """
    Case: close closed masternode.
    Expect: invalid transaction exception is raised with masternode is not opened or has been closed error message.
    """
    close_masternode_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.CLOSE_MASTERNODE
    transaction_payload.data = close_masternode_payload.SerializeToString()

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

    mock_context = create_context(account_from_balance=OPERATIONAL_BALANCE, node_state=NodeAccount.CLOSED,
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Masternode is not opened or has been closed.' == str(error.value)
