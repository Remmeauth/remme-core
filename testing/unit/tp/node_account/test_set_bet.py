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
    SetBetPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from testing.utils.client import proto_error_msg
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


def test_bet_configuration_set_fixed_amount():
    """
    Case: set bet config to node account as fixed_amount.
    Expect: update of node account state
    """
    set_bet_payload = SetBetPayload(
        fixed_amount=1
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.SET_BET
    transaction_payload.data = set_bet_payload.SerializeToString()

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

    node_account = state_as_dict.get(NODE_ACCOUNT_ADDRESS_FROM)

    assert node_account.max is False
    assert node_account.min is False
    assert node_account.fixed_amount is 1


def test_bet_configuration_set_max():
    """
    Case: set bet config to node account as max.
    Expect: update of node account state
    """
    set_bet_payload = SetBetPayload(
        max=True
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.SET_BET
    transaction_payload.data = set_bet_payload.SerializeToString()

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

    node_account = state_as_dict.get(NODE_ACCOUNT_ADDRESS_FROM)

    assert node_account.max is True
    assert node_account.min is False
    assert node_account.fixed_amount is 0


def test_bet_configuration_set_min():
    """
    Case: set bet config to node account as max.
    Expect: update of node account state
    """
    set_bet_payload = SetBetPayload(
        min=True
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.SET_BET
    transaction_payload.data = set_bet_payload.SerializeToString()

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

    node_account = state_as_dict.get(NODE_ACCOUNT_ADDRESS_FROM)

    assert node_account.max is False
    assert node_account.min is True
    assert node_account.fixed_amount is 0


def test_bet_configuration_set_no_data():
    """
    Case: set bet config to node account without data.
    Expect: error occured
    """
    set_bet_payload = SetBetPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.SET_BET
    transaction_payload.data = set_bet_payload.SerializeToString()

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

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        SetBetPayload,
        {
            'bet': ['At least one of fixed_amount, min or max must be set'],
        }
    ) == str(error.value)
