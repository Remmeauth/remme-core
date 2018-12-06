"""
Provide tests for account handler apply method implementation.
"""
import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.tp.account import AccountHandler
from remme.protos.account_pb2 import (
    Account,
    AccountMethod,
    TransferPayload,
)

from testing.conftest import create_transaction_request
from testing.mocks.stub import StubContext

ADDRESS_NOT_ACCOUNT_TYPE = '000000' + 'cfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

TOKENS_AMOUNT_TO_SEND = 1000

ACCOUNT_FROM_BALANCE = 10000
ACCOUNT_TO_BALANCE = 1000

ACCOUNT_ADDRESS_FROM = '112007d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
ACCOUNT_ADDRESS_TO = '1120071db7c02f5731d06df194dc95465e9b277c19e905ce642664a9a0d504a3909e31'

INPUTS = [
    ACCOUNT_ADDRESS_FROM,
    ACCOUNT_ADDRESS_TO,
]

OUTPUTS = [
    ACCOUNT_ADDRESS_FROM,
    ACCOUNT_ADDRESS_TO,
]

SENDER_PARAMETERS = {
    'address': ACCOUNT_ADDRESS_FROM,
    'private_key': '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4',
    'public_key': '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940',
}

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': AccountHandler().family_name,
    'family_version': AccountHandler()._family_versions[0],
}


def create_context(account_from_balance, account_to_balance):
    """
    Create stub context with initial data.

    Stub context is an interface around Sawtooth state, consider as database.
    State is key-value storage that contains address with its data (i.e. account balance).

    References:
        - https://github.com/Remmeauth/remme-core/blob/dev/testing/mocks/stub.py
    """
    account_protobuf = Account()

    account_protobuf.balance = account_from_balance
    serialized_account_from_balance = account_protobuf.SerializeToString()

    account_protobuf.balance = account_to_balance
    serialized_account_to_balance = account_protobuf.SerializeToString()

    initial_state = {
        ACCOUNT_ADDRESS_FROM: serialized_account_from_balance,
        ACCOUNT_ADDRESS_TO: serialized_account_to_balance,
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)


def test_transaction_request_account_handler():
    """
    Case: send transaction request to the account handler.
    Expect: addresses data, stored in state, are changed according to transfer amount.
    """
    expected_account_from_balance = ACCOUNT_FROM_BALANCE - TOKENS_AMOUNT_TO_SEND
    expected_account_to_balance = ACCOUNT_TO_BALANCE + TOKENS_AMOUNT_TO_SEND

    account_protobuf = Account()

    account_protobuf.balance = expected_account_from_balance
    expected_serialized_account_from_balance = account_protobuf.SerializeToString()

    account_protobuf.balance = expected_account_to_balance
    expected_serialized_account_to_balance = account_protobuf.SerializeToString()

    expected_state = {
        ACCOUNT_ADDRESS_FROM: expected_serialized_account_from_balance,
        ACCOUNT_ADDRESS_TO: expected_serialized_account_to_balance,
    }

    transaction_params = {
        'method': AccountMethod.TRANSFER,
    }

    transaction_request = create_transaction_request(
        sender_params=SENDER_PARAMETERS,
        address_to=ACCOUNT_ADDRESS_TO,
        amount=TOKENS_AMOUNT_TO_SEND,
        handler_params=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
        transaction_params=transaction_params,
    )

    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[ACCOUNT_ADDRESS_TO, ACCOUNT_ADDRESS_FROM])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_account_handler_not_available_transfer_method():
    """
    Case: send transaction request to the account handler with not available transfer method value.
    Expect:
    """
    account_method_impossible_value = 5347

    transaction_params = {
        'method': account_method_impossible_value,
    }

    transaction_request = create_transaction_request(
        sender_params=SENDER_PARAMETERS,
        address_to=ACCOUNT_ADDRESS_TO,
        amount=TOKENS_AMOUNT_TO_SEND,
        handler_params=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
        transaction_params=transaction_params,
    )

    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Unknown value {account_method_impossible_value} for the pub_key operation type.' == str(error.value)


def test_account_transfer_from_address():
    """
    Case: transfer tokens from address to address.
    Expect: account's balances, stored in state, are changed according to transfer amount.
    """
    expected_account_from_balance = ACCOUNT_FROM_BALANCE - TOKENS_AMOUNT_TO_SEND
    expected_account_to_balance = ACCOUNT_TO_BALANCE + TOKENS_AMOUNT_TO_SEND

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    result = AccountHandler()._transfer_from_address(
        context=mock_context, address=ACCOUNT_ADDRESS_FROM, transfer_payload=transfer_payload,
    )

    assert result.get(ACCOUNT_ADDRESS_FROM).balance == expected_account_from_balance
    assert result.get(ACCOUNT_ADDRESS_TO).balance == expected_account_to_balance


def test_account_transfer_from_address_zero_amount():
    """
    Case: transfer zero tokens from address to address.
    Expect: invalid transaction error is raised with could not transfer with zero amount error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = 0

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler()._transfer_from_address(
            context=mock_context, address=ACCOUNT_ADDRESS_FROM, transfer_payload=transfer_payload,
        )

    assert f'Could not transfer with zero amount.' == str(error.value)


def test_account_transfer_from_address_to_address_not_account_type():
    """
    Case: transfer tokens from address to address that is not account type.
    Expect: invalid transaction error is raised with receiver address is not account type error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ADDRESS_NOT_ACCOUNT_TYPE
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler()._transfer_from_address(
            context=mock_context, address=ACCOUNT_ADDRESS_FROM, transfer_payload=transfer_payload,
        )

    assert f'Receiver address has to be of an account type.' == str(error.value)


def test_account_transfer_from_address_send_to_itself():
    """
    Case: transfer tokens from address to the same address.
    Expect: invalid transaction error is raised account cannot send tokens to itself error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_FROM
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler()._transfer_from_address(
            context=mock_context, address=ACCOUNT_ADDRESS_FROM, transfer_payload=transfer_payload,
        )

    assert f'Account cannot send tokens to itself.' == str(error.value)


def test_account_transfer_from_address_without_tokens():
    """
    Case: transfer tokens from address with zero tokens amount to address.
    Expect: invalid transaction error is raised with not enough transferable balance error message.
    """
    mock_context = create_context(account_from_balance=0, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler()._transfer_from_address(
            context=mock_context, address=ACCOUNT_ADDRESS_FROM, transfer_payload=transfer_payload,
        )

    assert f'Not enough transferable balance. Sender\'s current balance: 0.' == str(error.value)
