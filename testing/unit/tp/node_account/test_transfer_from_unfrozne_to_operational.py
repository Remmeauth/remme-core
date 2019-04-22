"""
Provide tests for node account transferring from unfrozen to operational.
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
from remme.settings import TRANSACTION_FEE
from remme.shared.utils import hash512, client_to_real_amount
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.utils.client import proto_error_msg

from .shared import (
    RANDOM_NODE_PUBLIC_KEY,
    NODE_ACCOUNT_ADDRESS_FROM,
    NODE_ACCOUNT_FROM_PRIVATE_KEY,
    INPUTS,
    OUTPUTS,
    TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
    create_context,
)


def test_transfer_from_unfrozen_to_operational():
    """
    Case: transfer from unfrozen to operational.
    Expect: tokens are transferred.
    """
    unfrozen = 400000
    operational = 50000
    tokens_to_transfer = 50000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = tokens_to_transfer

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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=operational, node_state=NodeAccount.OPENED,
                                  unfrozen=unfrozen)

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

    assert node_account.balance == client_to_real_amount(operational + tokens_to_transfer - TRANSACTION_FEE)
    assert node_account.reputation.unfrozen == client_to_real_amount(unfrozen - tokens_to_transfer)


def test_transfer_invalid_amount_from_unfrozen_to_operational():
    """
    Case: transfer from unfrozen to operational with more tokens than on unfrozen account.
    Expect: invalid transaction exception is raised with invalid amount error message.
    """
    unfrozen = 400000
    operational = 50000
    tokens_to_transfer = 500000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = tokens_to_transfer

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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=operational, node_state=NodeAccount.OPENED,
                                  unfrozen=unfrozen)
    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert str(error.value) == 'Insufficient amount of tokens on unfrozen account.'


def test_transfer_from_unfrozen_to_operational_with_empty_proto():
    """
    Case: transfer from unfrozen to operational transaction with empty proto.
    Expect: invalid transaction exception with could not transfer with zero amount error message.
    """
    unfrozen = 400000
    operational = 50000

    internal_transfer_payload = NodeAccountInternalTransferPayload()

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
        signature=create_signer(private_key=NODE_ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(account_from_balance=operational, node_state=NodeAccount.OPENED,
                                  unfrozen=unfrozen)
    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        NodeAccountInternalTransferPayload,
        {
            'value': ['Could not transfer with zero amount.'],
        }
    ) == str(error.value)
