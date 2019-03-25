"""
Provide tests for account handler apply (genesis) method implementation.
"""
import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.setting_pb2 import Setting
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import SETTINGS_MINIMUM_STAKE
from remme.settings.helper import _make_settings_key
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg
from .shared import (
    MAX_UINT64
)

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

FROZEN = 600_000
UNFROZEN = 100_000
MINIMUM_STAKE = 250_000

NODE_ACCOUNT_ADDRESS_FROM = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'

NODE_ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT = _make_settings_key(SETTINGS_MINIMUM_STAKE)

INPUTS = OUTPUTS = [
    NODE_ACCOUNT_ADDRESS_FROM,
    ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT,
]

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': NodeAccountHandler().family_name,
    'family_version': NodeAccountHandler()._family_versions[0],
}


def create_context(account_from_frozen_balance, account_to_unfrozen_balance, minimum_stake=MINIMUM_STAKE):
    """
    Create stub context with initial data.

    Stub context is an interface around Sawtooth state, consider as database.
    State is key-value storage that contains address with its data (i.e. account balance).

    References:
        - https://github.com/Remmeauth/remme-core/blob/dev/testing/mocks/stub.py
    """
    node_account = NodeAccount()

    node_account.reputation.frozen = account_from_frozen_balance
    node_account.reputation.unfrozen = account_to_unfrozen_balance
    serialized_account_balance = node_account.SerializeToString()

    minimum_stake_setting = Setting()
    minimum_stake_setting.entries.add(key=SETTINGS_MINIMUM_STAKE, value=str(minimum_stake))
    serialized_minimum_stake_setting = minimum_stake_setting.SerializeToString()

    initial_state = {
        NODE_ACCOUNT_ADDRESS_FROM: serialized_account_balance,
        ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT: serialized_minimum_stake_setting,
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)


def test_account_handler_with_empty_proto():
    """
    Case: send transaction request with empty proto.
    Expect: invalid transaction error.
    """
    internal_transfer_payload = NodeAccountInternalTransferPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        NodeAccountInternalTransferPayload,
        {
            'value': ['Could not transfer with zero amount.'],
        }
    ) == str(error.value)


def test_transfer_from_frozen_to_unfrozen():
    """
    Case: send transaction request, to transfer tokens from reputational frozen balance to
          reputational unfrozen balance.
    Expect: frozen and unfrozen balances, stored in state, are changed according to transfer amount.
    """
    transfer_value = 10_000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = transfer_value

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = create_context(account_from_frozen_balance=FROZEN, account_to_unfrozen_balance=UNFROZEN)

    NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[NODE_ACCOUNT_ADDRESS_FROM])

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    node_account_reputation = state_as_dict.get(NODE_ACCOUNT_ADDRESS_FROM, NodeAccount()).reputation

    assert node_account_reputation.frozen == FROZEN - transfer_value
    assert node_account_reputation.unfrozen == UNFROZEN + transfer_value

def test_transfer_from_frozen_to_unfrozen_integer_overflow():
    """
    Case: transfer from frozen to unfrozen such that it will cause integer overflow.
    Expect: integer overflow exception is raised.
    """
    transfer_value = 1

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = transfer_value

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = create_context(account_from_frozen_balance=MINIMUM_STAKE+1, account_to_unfrozen_balance=MAX_UINT64)

    with pytest.raises(ValueError) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert str(error.value).startswith('Value out of range')

def test_transfer_from_frozen_to_unfrozen_low_frozen_balance():
    """
    Case: send transaction request, to transfer tokens from reputational frozen balance to reputational unfrozen balance
          with frozen balance < minimum stake.
    Expect: invalid transaction error is raised with frozen balance is lower than the minimum stake error message.
    """
    transfer_value = 10_000
    frozen_value = MINIMUM_STAKE - 10_000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = transfer_value

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = create_context(account_from_frozen_balance=frozen_value, account_to_unfrozen_balance=UNFROZEN)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Frozen balance is lower than the minimum stake.' == str(error.value)


def test_transfer_from_frozen_to_unfrozen_big_value():
    """
    Case: send transaction request, to transfer tokens from reputational frozen balance to
          reputational unfrozen balance with big transfer value.
    Expect: invalid transaction error is raised with the transfer amount too big error message.
    """
    transfer_value = 1_000_000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = transfer_value

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = create_context(account_from_frozen_balance=FROZEN, account_to_unfrozen_balance=UNFROZEN)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Frozen balance after transfer lower than the minimum stake.' == str(error.value)


def test_transfer_from_frozen_to_unfrozen_malformed_minimum_stake():
    """
    Case: send transaction request, to transfer tokens from reputational frozen balance to
          reputational unfrozen balance with malformed minimum stake.
    Expect: invalid transaction error is raised with wrong minimum stake address error message.
    """
    transfer_value = 10_000

    internal_transfer_payload = NodeAccountInternalTransferPayload()
    internal_transfer_payload.value = transfer_value

    transaction_payload = TransactionPayload()
    transaction_payload.method = NodeAccountMethod.TRANSFER_FROM_FROZEN_TO_UNFROZEN
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

    mock_context = create_context(account_from_frozen_balance=FROZEN,
                                  account_to_unfrozen_balance=UNFROZEN,
                                  minimum_stake=-1)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Wrong minimum stake address.' == str(error.value)
