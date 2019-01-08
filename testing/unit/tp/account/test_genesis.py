"""
Provide tests for account handler (transfer) apply method implementation.
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
    GenesisPayload,
    GenesisStatus,
    TransferPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.tp.account import AccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

TOKENS_AMOUNT_TO_SUPPLY = 1_000_000

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': AccountHandler().family_name,
    'family_version': AccountHandler()._family_versions[0],
}

GENESIS_ADDRESS = '0000000000000000000000000000000000000000000000000000000000000000000001'
ACCOUNT_ADDRESS_TO= '112007d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'

INPUTS = OUTPUTS = [
    GENESIS_ADDRESS,
    ACCOUNT_ADDRESS_TO,
]

NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
NODE_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'


def test_account_handler_genesis_apply_with_empty_proto():
    """
    Case: send transaction request of genesis with empty proto
    Expect: invalid transaction error
    """
    genesis_payload = GenesisPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.GENESIS
    transaction_payload.data = genesis_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=NODE_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        GenesisPayload,
        {'total_supply': ['This field is required.']}
    ) == str(error.value)


def test_account_handler_genesis_apply():
    """
    Case: send transaction request, to send tokens from genesis address, to the account handler.
    Expect:
    """
    account = Account()
    account.balance = TOKENS_AMOUNT_TO_SUPPLY
    expected_serialized_account_to_balance = account.SerializeToString()

    genesis_payload = GenesisPayload()
    genesis_payload.total_supply = TOKENS_AMOUNT_TO_SUPPLY

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.GENESIS
    transaction_payload.data = genesis_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=NODE_PRIVATE_KEY).sign(serialized_header),
    )

    genesis_status = GenesisStatus()
    genesis_status.status = True

    expected_state = {
        GENESIS_ADDRESS: genesis_status.SerializeToString(),
        ACCOUNT_ADDRESS_TO: expected_serialized_account_to_balance,
    }

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[GENESIS_ADDRESS, ACCOUNT_ADDRESS_TO])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_account_handler_genesis_already_initialized():
    """
    Case: send transaction request, to send tokens from genesis address,
        to the account handler when genesis was already initialized.
    Expect: invalid transaction error is raised with genesis is already initialized error message.
    """
    genesis_payload = GenesisPayload()
    genesis_payload.total_supply = TOKENS_AMOUNT_TO_SUPPLY

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.GENESIS
    transaction_payload.data = genesis_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=NODE_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=NODE_PRIVATE_KEY).sign(serialized_header),
    )

    genesis_status = GenesisStatus()
    genesis_status.status = True

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        GENESIS_ADDRESS: genesis_status.SerializeToString()
    })

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Genesis is already initialized.' == str(error.value)
