"""
Provide tests for account handler apply method implementation.
"""
from remme.tp.account import AccountHandler
from remme.protos.account_pb2 import Account

from testing.conftest import create_transaction_request
from testing.mocks.stub import StubContext


def test_transaction_request_account_handler():
    """
    Case: send transaction request to the account handler.
    Expect: addresses balances, stored in state (consider as database), are changed according to transfer amount.
    """
    tokens_amount_to_send = 1000

    account_protobuf = Account()

    account_protobuf.balance = 10000
    serialized_account_from_balance = account_protobuf.SerializeToString()

    account_protobuf.balance -= tokens_amount_to_send
    serialized_account_to_balance = account_protobuf.SerializeToString()

    account_protobuf.balance = 9000
    expected_serialized_account_from_balance = account_protobuf.SerializeToString()

    account_protobuf.balance += tokens_amount_to_send
    expected_serialized_account_to_balance = account_protobuf.SerializeToString()

    address_from = '112007d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
    address_to = '1120071db7c02f5731d06df194dc95465e9b277c19e905ce642664a9a0d504a3909e31'

    inputs = [
        address_from,
        address_to,
    ]

    outputs = [
        address_from,
        address_to,
    ]

    initial_state = {
        address_from: serialized_account_from_balance,
        address_to: serialized_account_to_balance,
    }

    expected_state = {
        address_from: expected_serialized_account_from_balance,
        address_to: expected_serialized_account_to_balance,
    }

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state=initial_state)

    sender_params = {
        'address': address_from,
        'private_key': '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4',
        'public_key': '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940',
    }

    transaction_request_handler_params = {
        'family_name': AccountHandler().family_name,
        'family_version': AccountHandler()._family_versions.pop(),
    }

    transaction_request = create_transaction_request(
        sender_params=sender_params,
        address_to=address_to,
        amount=tokens_amount_to_send,
        handler_params=transaction_request_handler_params,
    )

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[address_to, address_from])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict
