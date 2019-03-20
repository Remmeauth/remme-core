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

from remme.protos.account_pb2 import (
    Account,
    AccountMethod,
    TransferPayload,
)
from remme.protos.node_account_pb2 import (
    NodeAccount,
)
from remme.settings import SETTINGS_TRANSACTION_FEE, ZERO_ADDRESS
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.settings.helper import _make_settings_key
from remme.tp.account import AccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236942'

ADDRESS_NOT_ACCOUNT_TYPE = '000000' + 'cfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

TOKENS_AMOUNT_TO_SEND = 1000

ACCOUNT_FROM_BALANCE = NODE_ACCOUNT_FROM_BALANCE = 10000
ACCOUNT_TO_BALANCE = NODE_ACCOUNT_TO_BALANCE = 1000

TRANSACTION_FEE_AMOUNT = 0.0010

ACCOUNT_ADDRESS_FROM = '112007d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
ACCOUNT_ADDRESS_TO = '1120071db7c02f5731d06df194dc95465e9b277c19e905ce642664a9a0d504a3909e31'

ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
ACCOUNT_FROM_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT = _make_settings_key(SETTINGS_TRANSACTION_FEE)

INPUTS = OUTPUTS = [
    ACCOUNT_ADDRESS_FROM,
    ACCOUNT_ADDRESS_TO,
    ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT,
    ZERO_ADDRESS,
]

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

    transaction_fee_setting = Setting()
    transaction_fee_setting.entries.add(key=SETTINGS_TRANSACTION_FEE, value=str(TRANSACTION_FEE_AMOUNT))
    serialized_transaction_fee_setting = transaction_fee_setting.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    initial_state = {
        ACCOUNT_ADDRESS_FROM: serialized_account_from_balance,
        ACCOUNT_ADDRESS_TO: serialized_account_to_balance,
        ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT: serialized_transaction_fee_setting,
        ZERO_ADDRESS: serialized_zero_account,
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)


def test_account_handler_with_empty_proto():
    """
    Case: send transaction request with empty proto
    Expect: invalid transaction error
    """
    transfer_payload = TransferPayload()

    transaction_payload = TransactionPayload()
    transfer_payload.sender_account_type = 1337
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        TransferPayload,
        {
            'sender_account_type': ['Not a valid choice'],
            'address_to': ['Missed address.'],
            'value': ['Could not transfer with zero amount.'],
        }
    ) == str(error.value)


def test_account_handler_apply():
    """
    Case: send transaction request, to send tokens to address, to the account handler.
    Expect: addresses data, stored in state, are changed according to transfer amount.
    """
    transfer_commission = int(TOKENS_AMOUNT_TO_SEND * TRANSACTION_FEE_AMOUNT)
    tokens_amount_to_send_total = TOKENS_AMOUNT_TO_SEND + transfer_commission
    expected_account_from_balance = ACCOUNT_FROM_BALANCE - tokens_amount_to_send_total
    expected_account_to_balance = ACCOUNT_TO_BALANCE + TOKENS_AMOUNT_TO_SEND

    account_protobuf = Account()

    account_protobuf.balance = expected_account_from_balance
    expected_serialized_account_from_balance = account_protobuf.SerializeToString()

    account_protobuf.balance = expected_account_to_balance
    expected_serialized_account_to_balance = account_protobuf.SerializeToString()

    account_protobuf.balance = transfer_commission
    expected_serialized_zero_address_balance = account_protobuf.SerializeToString()

    expected_state = {
        ACCOUNT_ADDRESS_FROM: expected_serialized_account_from_balance,
        ACCOUNT_ADDRESS_TO: expected_serialized_account_to_balance,
        ZERO_ADDRESS: expected_serialized_zero_address_balance
    }

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[ACCOUNT_ADDRESS_TO, ACCOUNT_ADDRESS_FROM, ZERO_ADDRESS])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_account_handler_apply_invalid_transfer_method():
    """
    Case: send transaction request, to send tokens to address, to account handler with invalid transfer method value.
    Expect: invalid transaction error is raised with invalid account method value error message.
    """
    account_method_impossible_value = 5347

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = account_method_impossible_value
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Invalid account method value ({account_method_impossible_value}) has been set.' == str(error.value)


def test_account_handler_apply_decode_error():
    """
    Case: send transaction request, to send tokens to address, to account handler with invalid transaction payload.
    Expect: invalid transaction error is raised cannot decode transaction payload error message.
    """
    serialized_not_valid_transaction_payload = b'F1120071db7c02f5731d06df194dc95465e9b27'

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_not_valid_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_not_valid_transaction_payload,
        signature=create_signer(private_key=ACCOUNT_FROM_PRIVATE_KEY).sign(serialized_header),
    )
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Cannot decode transaction payload.' == str(error.value)


def test_account_transfer_from_address():
    """
    Case: transfer tokens from address to address.
    Expect: account's balances, stored in state, are changed according to transfer amount.
    """
    transfer_commission = int(TOKENS_AMOUNT_TO_SEND * TRANSACTION_FEE_AMOUNT)
    tokens_amount_to_send_total = TOKENS_AMOUNT_TO_SEND + transfer_commission
    expected_account_from_balance = ACCOUNT_FROM_BALANCE - tokens_amount_to_send_total
    expected_account_to_balance = ACCOUNT_TO_BALANCE + TOKENS_AMOUNT_TO_SEND

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ACCOUNT_ADDRESS_FROM,
        ACCOUNT_ADDRESS_TO,
        ZERO_ADDRESS,
    ])

    state_as_dict = {}
    for entry in state_as_list:
        acc = Account()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    assert state_as_dict.get(ACCOUNT_ADDRESS_FROM, Account()).balance == expected_account_from_balance
    assert state_as_dict.get(ACCOUNT_ADDRESS_TO, Account()).balance == expected_account_to_balance
    assert state_as_dict.get(ZERO_ADDRESS, Account()).balance == transfer_commission


def test_account_transfer_from_address_zero_amount():
    """
    Case: transfer zero tokens from address to address.
    Expect: invalid transaction error is raised with could not transfer with zero amount error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = 0

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        TransferPayload,
        {
            'value': ['Could not transfer with zero amount.'],
        }
    ) == str(error.value)


def test_account_transfer_from_address_to_address_not_account_type():
    """
    Case: transfer tokens from address to address that is not account type.
    Expect: invalid transaction error is raised with receiver address is not account type error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ADDRESS_NOT_ACCOUNT_TYPE
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        TransferPayload,
        {
            'address_to': ['Address is not of a blockchain token type.'],
        }
    ) == str(error.value)


def test_account_transfer_from_address_send_to_itself():
    """
    Case: transfer tokens from address to the same address.
    Expect: invalid transaction error is raised with account cannot send tokens to itself error message.
    """
    mock_context = create_context(account_from_balance=ACCOUNT_FROM_BALANCE, account_to_balance=ACCOUNT_TO_BALANCE)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_FROM
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

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

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Not enough transferable balance. Sender\'s current balance: 0.' == str(error.value)


def test_account_transfer_from_address_without_previous_usage():
    """
    Case: transfer tokens from address to address when them have never been used before.
    Expect: invalid transaction error is raised with not enough transferable balance error message.
    """
    transaction_fee_setting = Setting()
    transaction_fee_setting.entries.add(key=SETTINGS_TRANSACTION_FEE, value=str(TRANSACTION_FEE_AMOUNT))
    serialized_transaction_fee_setting = transaction_fee_setting.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    initial_state = {
        ACCOUNT_ADDRESS_FROM: None,
        ACCOUNT_ADDRESS_TO: None,
        ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT: serialized_transaction_fee_setting,
        ZERO_ADDRESS: serialized_zero_account,
    }

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Not enough transferable balance. Sender\'s current balance: 0.' == str(error.value)


def test_node_account_transfer():
    """
    Case: send transaction request to send tokens to node account from node account.
    Expect: addresses data, stored in state, are changed according to transfer amount.
    """
    node_account_from_address_ = '116829' + '0abcb27dcbecb77a6ae3ae951f878cebd2fd94b07c4e21c54a49da0f57b81a65'
    node_account_to_address = '116829' + '5026f956719c91b87198f6762e680391c1023d19da5fad9380fc026300e52ac8'

    node_account_private_key_from = '45a514955de0808f1fa0f38319ade0052bd36de91ae024c3422e6e9222e10604'
    node_account_public_key_from = '0264f55d9e971961864a36a1a974d64cd8e76a8a07feb9f6a963e8923d0406c81d'

    inputs = outputs = [
        node_account_from_address_,
        node_account_to_address,
        ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT,
        ZERO_ADDRESS,
    ]

    transfer_commission = int(TOKENS_AMOUNT_TO_SEND * TRANSACTION_FEE_AMOUNT)
    tokens_amount_to_send_total = TOKENS_AMOUNT_TO_SEND + transfer_commission

    node_account_from = NodeAccount()
    node_account_from.balance = NODE_ACCOUNT_FROM_BALANCE - tokens_amount_to_send_total
    expected_serialized_node_account_from_balance = node_account_from.SerializeToString()

    node_account_to = NodeAccount()
    node_account_to.balance = NODE_ACCOUNT_TO_BALANCE + TOKENS_AMOUNT_TO_SEND
    expected_serialized_node_account_to_balance = node_account_to.SerializeToString()

    zero_account = Account()
    zero_account.balance = transfer_commission
    serialized_zero_account_balance = zero_account.SerializeToString()

    expected_state = {
        node_account_from_address_: expected_serialized_node_account_from_balance,
        node_account_to_address: expected_serialized_node_account_to_balance,
        ZERO_ADDRESS: serialized_zero_account_balance,
    }

    transfer_payload = TransferPayload()
    transfer_payload.sender_account_type = TransferPayload.NODE_ACCOUNT
    transfer_payload.address_to = node_account_to_address
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=node_account_public_key_from,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=inputs,
        outputs=outputs,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=node_account_private_key_from).sign(serialized_header),
    )

    node_account_from = NodeAccount()
    node_account_from.balance = NODE_ACCOUNT_FROM_BALANCE
    serialized_node_account_from_balance = node_account_from.SerializeToString()

    node_account_to = NodeAccount()
    node_account_to.balance = NODE_ACCOUNT_TO_BALANCE
    serialized_node_account_to_balance = node_account_to.SerializeToString()

    transaction_fee_setting = Setting()
    transaction_fee_setting.entries.add(key=SETTINGS_TRANSACTION_FEE, value=str(TRANSACTION_FEE_AMOUNT))
    serialized_transaction_fee_setting = transaction_fee_setting.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    initial_state = {
        node_account_from_address_: serialized_node_account_from_balance,
        node_account_to_address: serialized_node_account_to_balance,
        ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT: serialized_transaction_fee_setting,
        ZERO_ADDRESS: serialized_zero_account,
    }

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state=initial_state)

    AccountHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[node_account_from_address_,
                                                      node_account_to_address,
                                                      ZERO_ADDRESS])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_account_transfer_without_enough_amount_pay_commission():
    """
    Case: send transaction request to send tokens to account from account without enough amount pay commission.
    Expect: invalid transaction error is raised with not enough transferable balance error message.
    """
    account_from_balance = 1000

    transfer_payload = TransferPayload()
    transfer_payload.address_to = ACCOUNT_ADDRESS_TO
    transfer_payload.value = TOKENS_AMOUNT_TO_SEND

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ACCOUNT_FROM_PUBLIC_KEY,
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

    account_from = Account()
    account_from.balance = account_from_balance
    serialized_account_from_balance = account_from.SerializeToString()

    account_to = Account()
    account_to.balance = ACCOUNT_TO_BALANCE
    serialized_account_to_balance = account_to.SerializeToString()

    transaction_fee_setting = Setting()
    transaction_fee_setting.entries.add(key=SETTINGS_TRANSACTION_FEE, value=str(TRANSACTION_FEE_AMOUNT))
    serialized_transaction_fee_setting = transaction_fee_setting.SerializeToString()

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    initial_state = {
        ACCOUNT_ADDRESS_FROM: serialized_account_from_balance,
        ACCOUNT_ADDRESS_TO: serialized_account_to_balance,
        ADDRESS_TO_GET_TRANSACTION_FEE_AMOUNT: serialized_transaction_fee_setting,
        ZERO_ADDRESS: serialized_zero_account,
    }

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)

    with pytest.raises(InvalidTransaction) as error:
        AccountHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Not enough transferable balance. Sender\'s current balance: 1000.' == str(error.value)
