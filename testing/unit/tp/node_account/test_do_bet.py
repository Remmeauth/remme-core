import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)
from remme.protos.account_pb2 import Account
from remme.protos.node_account_pb2 import (
    NodeAccountMethod,
    NodeAccount,
)
from remme.protos.transaction_pb2 import TransactionPayload, EmptyPayload
from remme.shared.utils import hash512
from remme.tp.internal import InternalHandler
from remme.tp.consensus_account import ConsensusAccountHandler, ConsensusAccount
from testing.utils.client import proto_error_msg
from testing.conftest import create_signer

from .shared import (
    RANDOM_NODE_PUBLIC_KEY,
    NODE_ACCOUNT_ADDRESS_FROM,
    NODE_ACCOUNT_FROM_PRIVATE_KEY,
    INPUTS,
    OUTPUTS,
    create_context,
    BLOCK_COST,
    ZERO_ADDRESS,
)


FROZEN_BALANCE = 300000
UNFROZEN_BALANCE = 10000
OPERATIONAL_BALANCE = 5000

TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS = {
    'family_name': InternalHandler().family_name,
    'family_version': InternalHandler().family_versions[0],
}


def test_do_bet_min():
    """
    Case: do bet for min condition.
    Expect: update of consensus account state
    """
    payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.DO_BET
    transaction_payload.data = payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_version'),
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
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE, min=True)

    InternalHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        ZERO_ADDRESS,
        NODE_ACCOUNT_ADDRESS_FROM,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    zero_acc = Account()
    zero_acc.ParseFromString(state_as_dict[ZERO_ADDRESS])

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_ADDRESS_FROM])

    assert node_acc.balance == OPERATIONAL_BALANCE - BLOCK_COST

    assert NODE_ACCOUNT_ADDRESS_FROM in consensus_acc.bets
    assert consensus_acc.bets[NODE_ACCOUNT_ADDRESS_FROM] == BLOCK_COST


def test_do_bet_max():
    """
    Case: do bet for max condition.
    Expect: update of consensus account state
    """
    payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.DO_BET
    transaction_payload.data = payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_version'),
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
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE, max=True)

    InternalHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        ZERO_ADDRESS,
        NODE_ACCOUNT_ADDRESS_FROM,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    zero_acc = Account()
    zero_acc.ParseFromString(state_as_dict[ZERO_ADDRESS])

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_ADDRESS_FROM])

    assert node_acc.balance == OPERATIONAL_BALANCE - 9 * BLOCK_COST

    assert NODE_ACCOUNT_ADDRESS_FROM in consensus_acc.bets
    assert consensus_acc.bets[NODE_ACCOUNT_ADDRESS_FROM] == 9 * BLOCK_COST


def test_do_bet_fixed_amount():
    """
    Case: do bet for fixed_amount condition.
    Expect: update of consensus account state
    """
    payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.DO_BET
    transaction_payload.data = payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_INTERNAL_HANDLER_PARAMS.get('family_version'),
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

    FIXED_AMOUNT = 4

    mock_context = create_context(account_from_balance=OPERATIONAL_BALANCE, node_state=NodeAccount.OPENED,
                                  frozen=FROZEN_BALANCE, unfrozen=UNFROZEN_BALANCE, fixed_amount=FIXED_AMOUNT)

    InternalHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        ZERO_ADDRESS,
        NODE_ACCOUNT_ADDRESS_FROM,
    ])

    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    zero_acc = Account()
    zero_acc.ParseFromString(state_as_dict[ZERO_ADDRESS])

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_ADDRESS_FROM])

    assert node_acc.balance == OPERATIONAL_BALANCE - FIXED_AMOUNT * BLOCK_COST

    assert NODE_ACCOUNT_ADDRESS_FROM in consensus_acc.bets
    assert consensus_acc.bets[NODE_ACCOUNT_ADDRESS_FROM] == FIXED_AMOUNT * BLOCK_COST
