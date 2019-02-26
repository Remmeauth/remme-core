"""
Provide tests for node account transferring from unfrozen to operational
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
    NodeAccountInternalTransferPayload, NodeAccountMethod, NodeAccount
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import ZERO_ADDRESS
from remme.shared.utils import hash512
from remme.tp.account import AccountHandler
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

from .shared import *


def test_transfer_from_unfrozen_to_operational():
    """
    Case: transfer from unfrozen to operational
    Expect: tokens are transferred
    """
    UNFROZEN = 400000
    OPERATIONAL = 50000
    TOKENS_TO_TRANSFER = 50000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = TOKENS_TO_TRANSFER

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL
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
                                  unfrozen=UNFROZEN)

    NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ACCOUNT_ADDRESS_FROM
    ])

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).balance == OPERATIONAL + TOKENS_TO_TRANSFER
    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation.unfrozen == UNFROZEN - TOKENS_TO_TRANSFER


def test_transfer_invalid_amount_from_unfrozen_to_operational():
    """
    Case: transfer from unfrozen to operational with more tokens than on unfrozen account
    Expect: Exception: Invalid amount.
            tokens are not transferred
    """
    UNFROZEN = 400000
    OPERATIONAL = 50000
    TOKENS_TO_TRANSFER = 500000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = TOKENS_TO_TRANSFER

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL
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
                                  unfrozen=UNFROZEN)
    with pytest.raises(ValueError) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert str(error.value).startswith('Value out of range:')
