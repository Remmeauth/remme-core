import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.consensus_account_pb2 import (
    ConsensusAccountMethod,
    ConsensusAccount,
)
from remme.protos.transaction_pb2 import TransactionPayload, EmptyPayload
from remme.shared.utils import hash512, client_to_real_amount
from remme.tp.consensus_account import ConsensusAccountHandler
from testing.utils.client import proto_error_msg
from testing.conftest import create_signer

from .shared import *


def test_send_reward_less_condition():
    """
    Case: test for _send_reward method when rep < init_stake
    Expect: update of a state
    """
    empty_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ConsensusAccountMethod.SEND_REWARD
    transaction_payload.data = empty_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_version'),
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
        signature=create_signer(private_key=NODE_ACCOUNT_SIGNER_PRIVATE_KEY).sign(serialized_header),
    )

    BLOCK_COST = 10
    OBLIGATORY_PAYMENTS = 10
    BET_VALUE = 10

    REW = BLOCK_COST + OBLIGATORY_PAYMENTS + BET_VALUE

    NODE_REW = 0.9 * REW
    REMME_REW = REW - NODE_REW

    mock_context = create_context(node_state=NodeAccount.OPENED,
                                  block_cost=BLOCK_COST,
                                  obligatory_payments=OBLIGATORY_PAYMENTS,
                                  bet_value=BET_VALUE)

    ConsensusAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        NODE_ACCOUNT_SIGNER_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        GENESIS_ACCOUNT_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_SIGNER_ADDRESS])

    genesis_acc = Account()
    genesis_acc.ParseFromString(state_as_dict[GENESIS_ACCOUNT_ADDRESS])

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    assert node_acc.reputation.frozen == client_to_real_amount(NODE_REW)
    assert node_acc.reputation.unfrozen == 0
    assert genesis_acc.balance == client_to_real_amount(REMME_REW)

    assert consensus_acc.block_cost == 0
    assert consensus_acc.obligatory_payments == 0
    assert NODE_ACCOUNT_SIGNER_ADDRESS not in consensus_acc.bets

    share = node_acc.shares[0]
    assert share.frozen_share == client_to_real_amount(0.9)
    assert share.block_timestamp == CURRENT_TIMESTAMP
    assert share.block_num == 1000
    assert share.reward == client_to_real_amount(REW)
    assert share.defrost_months == 0


def test_send_reward_upper_condition():
    """
    Case: test for _send_reward method when init_stake <= rep < init_stake * min_stake
    Expect: update of a state
    """
    empty_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ConsensusAccountMethod.SEND_REWARD
    transaction_payload.data = empty_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_version'),
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
        signature=create_signer(private_key=NODE_ACCOUNT_SIGNER_PRIVATE_KEY).sign(serialized_header),
    )

    FROZEN = 120_000
    UNFROZEN = 180_000

    BLOCK_COST = 10
    OBLIGATORY_PAYMENTS = 10
    BET_VALUE = 10

    REW = BLOCK_COST + OBLIGATORY_PAYMENTS + BET_VALUE

    NODE_REW = 0.9 * REW
    REMME_REW = REW - NODE_REW

    UNODE_REW = 0.46 * REW
    FNODE_REW = REW - UNODE_REW

    mock_context = create_context(node_state=NodeAccount.OPENED,
                                  block_cost=BLOCK_COST,
                                  obligatory_payments=OBLIGATORY_PAYMENTS,
                                  bet_value=BET_VALUE,
                                  frozen=FROZEN,
                                  unfrozen=UNFROZEN)

    ConsensusAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        NODE_ACCOUNT_SIGNER_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        GENESIS_ACCOUNT_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_SIGNER_ADDRESS])

    genesis_acc = Account()
    genesis_acc.ParseFromString(state_as_dict[GENESIS_ACCOUNT_ADDRESS])

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    assert node_acc.reputation.unfrozen == client_to_real_amount(UNODE_REW + UNFROZEN)
    assert node_acc.reputation.frozen == client_to_real_amount(FNODE_REW + FROZEN)
    assert genesis_acc.balance == client_to_real_amount(REMME_REW)

    assert consensus_acc.block_cost == 0
    assert consensus_acc.obligatory_payments == 0
    assert NODE_ACCOUNT_SIGNER_ADDRESS not in consensus_acc.bets

    share = node_acc.shares[0]
    assert share.frozen_share == client_to_real_amount(0.9 - 0.46)
    assert share.block_timestamp == CURRENT_TIMESTAMP
    assert share.block_num == 1000
    assert share.reward == client_to_real_amount(REW)
    assert share.defrost_months == 0


def test_send_reward_middle_condition():
    """
    Case: test for _send_reward method when reputational >= min_stake * initial_stake
    Expect: update of a state
    """
    empty_payload = EmptyPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ConsensusAccountMethod.SEND_REWARD
    transaction_payload.data = empty_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=RANDOM_NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS.get('family_version'),
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
        signature=create_signer(private_key=NODE_ACCOUNT_SIGNER_PRIVATE_KEY).sign(serialized_header),
    )

    FROZEN = 250_000 * 5
    UNFROZEN = 250_000 * 6

    BLOCK_COST = 10
    OBLIGATORY_PAYMENTS = 10
    BET_VALUE = 10

    REW = BLOCK_COST + OBLIGATORY_PAYMENTS + BET_VALUE

    NODE_REW = 0.9 * REW
    REMME_REW = REW - NODE_REW

    mock_context = create_context(node_state=NodeAccount.OPENED,
                                  block_cost=BLOCK_COST,
                                  obligatory_payments=OBLIGATORY_PAYMENTS,
                                  bet_value=BET_VALUE,
                                  frozen=FROZEN,
                                  unfrozen=UNFROZEN)

    ConsensusAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        NODE_ACCOUNT_SIGNER_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        GENESIS_ACCOUNT_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    node_acc = NodeAccount()
    node_acc.ParseFromString(state_as_dict[NODE_ACCOUNT_SIGNER_ADDRESS])

    genesis_acc = Account()
    genesis_acc.ParseFromString(state_as_dict[GENESIS_ACCOUNT_ADDRESS])

    consensus_acc = ConsensusAccount()
    consensus_acc.ParseFromString(state_as_dict[ConsensusAccountHandler.CONSENSUS_ADDRESS])

    assert node_acc.reputation.frozen == client_to_real_amount(FROZEN)
    assert node_acc.reputation.unfrozen == client_to_real_amount(NODE_REW + UNFROZEN)
    assert genesis_acc.balance == client_to_real_amount(REMME_REW)

    assert consensus_acc.block_cost == 0
    assert consensus_acc.obligatory_payments == 0
    assert NODE_ACCOUNT_SIGNER_ADDRESS not in consensus_acc.bets

    assert not node_acc.shares
