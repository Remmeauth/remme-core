"""
Provide tests for atomic swap handler closing method implementation.
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

from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg
from remme.protos.atomic_swap_pb2 import (
    AtomicSwapInfo,
    AtomicSwapClosePayload,
    AtomicSwapMethod,
)
from remme.protos.account_pb2 import Account
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings.helper import _make_settings_key
from remme.shared.utils import hash512, web3_hash
from remme.tp.atomic_swap import AtomicSwapHandler
from remme.tp.basic import BasicHandler

from remme.settings import (
    SETTINGS_KEY_ZERO_ADDRESS_OWNERS,
    ZERO_ADDRESS,
)

TOKENS_AMOUNT_TO_SWAP = 200
SWAP_COMMISSION_AMOUNT = 100

BOT_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'
BOT_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
BOT_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'

ALICE_PRIVATE_KEY = '8c87d914a6cfeaf027413760ad359b5a56bfe0eda504d879b21872c7dc5b911c'
ALICE_PUBLIC_KEY = '02feb988591c78e58e57cdce5a314bd04798971227fcc2316907355392a2c99c25'
ALICE_ADDRESS = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'

FALSE_SECRET_KEY = '3e0b064c97249922a3b345ce7b2a8987d947283cb2871c26db4c2599a13e58e61'
SECRET_KEY = '3e0b064c97247732a3b345ce7b2a835d928623cb2871c26db4c2539a38e61a16'
SECRET_LOCK = web3_hash(SECRET_KEY)

SWAP_ID = '033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3884'

ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY = _make_settings_key(SETTINGS_KEY_ZERO_ADDRESS_OWNERS)
ADDRESS_TO_STORE_SWAP_INFO_BY = BasicHandler(
    name=AtomicSwapHandler().family_name, versions=AtomicSwapHandler()._family_versions[0]
).make_address_from_data(data=SWAP_ID)


TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': AtomicSwapHandler().family_name,
    'family_version': AtomicSwapHandler()._family_versions[0],
}

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
RANDOM_PUBLIC_KEY = '8c87d914a6cfeaf027413760ad359b5a56bfe0eda504d879b21872c7dc5b911c'

INPUTS = OUTPUTS = [
    ADDRESS_TO_STORE_SWAP_INFO_BY,
    ALICE_ADDRESS,
]


def test_close_with_empty_proto():
    """
    Case: send empty proto for close
    Expect: invalid transaction error
    """
    atomic_swap_init_payload = AtomicSwapClosePayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_init_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        AtomicSwapClosePayload,
        {
            'swap_id': ['Missed swap_id'],
            'secret_key': ['This field is required.'],
        }
    ) == str(error.value)


def test_close_atomic_swap():
    """
    Case: close atomic swap.
    Expect: increase Alice account address by swap amount.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    alice_account = Account()
    alice_account.balance = 0
    serialized_alice_account = alice_account.SerializeToString()

    existing_swap_info_to_close = AtomicSwapInfo()
    existing_swap_info_to_close.swap_id = SWAP_ID
    existing_swap_info_to_close.amount = 200
    existing_swap_info_to_close.state = AtomicSwapInfo.APPROVED
    existing_swap_info_to_close.secret_lock = SECRET_LOCK
    existing_swap_info_to_close.is_initiator = True
    existing_swap_info_to_close.sender_address = BOT_ADDRESS
    existing_swap_info_to_close.receiver_address = ALICE_ADDRESS
    serialized_existing_swap_info_to_lock = existing_swap_info_to_close.SerializeToString()

    genesis_members_setting = Setting()
    genesis_members_setting.entries.add(key=SETTINGS_KEY_ZERO_ADDRESS_OWNERS, value=f'{BOT_PUBLIC_KEY},')
    serialized_genesis_members_setting = genesis_members_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY: serialized_genesis_members_setting,
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_lock,
        ALICE_ADDRESS: serialized_alice_account,
    })

    expected_alice_account = Account()
    expected_alice_account.balance = TOKENS_AMOUNT_TO_SWAP
    serialized_expected_alice_account = expected_alice_account.SerializeToString()

    expected_closed_swap_info = AtomicSwapInfo()
    expected_closed_swap_info.swap_id = SWAP_ID
    expected_closed_swap_info.amount = 200
    expected_closed_swap_info.state = AtomicSwapInfo.CLOSED
    expected_closed_swap_info.secret_lock = SECRET_LOCK
    expected_closed_swap_info.secret_key = SECRET_KEY
    expected_closed_swap_info.is_initiator = True
    expected_closed_swap_info.sender_address = BOT_ADDRESS
    expected_closed_swap_info.receiver_address = ALICE_ADDRESS
    serialized_expected_closed_swap_info = expected_closed_swap_info.SerializeToString()

    expected_state = {
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_expected_closed_swap_info,
        ALICE_ADDRESS: serialized_expected_alice_account,
    }

    AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[ADDRESS_TO_STORE_SWAP_INFO_BY, ALICE_ADDRESS])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_close_not_initialized_atomic_swap():
    """
    Case: close not initialized atomic swap.
    Expect: invalid transaction error is raised with atomic swap was not initiated error message.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Atomic swap was not initiated for identifier {SWAP_ID}!' == str(error.value)


def test_close_already_closed_atomic_swap():
    """
    Case: close already closed atomic swap.
    Expect: invalid transaction error is raised with already operation with closed or expired swap error message.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    already_closed_swap_info = AtomicSwapInfo()
    already_closed_swap_info.swap_id = SWAP_ID
    already_closed_swap_info.state = AtomicSwapInfo.CLOSED
    serialized_already_closed_swap_info = already_closed_swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_already_closed_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'No operations can be done upon the swap: {SWAP_ID} as it is already closed or expired.' == str(error.value)


def test_close_atomic_swap_without_secret_lock():
    """
    Case: close swap without secret key.
    Expect: invalid transaction error is raised with secret lock is required to close the swap error message.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info_to_close = AtomicSwapInfo()
    existing_swap_info_to_close.swap_id = SWAP_ID
    existing_swap_info_to_close.state = AtomicSwapInfo.OPENED
    serialized_existing_swap_info_to_lock = existing_swap_info_to_close.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_lock,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Secret lock is required to close the swap.' == str(error.value)


def test_close_atomic_swap_with_false_secret_key():
    """
    Case: close swap with false secret key.
    Expect: invalid transaction error is raised with secret key does not match specified secret lock error message.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=FALSE_SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info_to_close = AtomicSwapInfo()
    existing_swap_info_to_close.swap_id = SWAP_ID
    existing_swap_info_to_close.state = AtomicSwapInfo.OPENED
    existing_swap_info_to_close.secret_lock = SECRET_LOCK
    serialized_existing_swap_info_to_lock = existing_swap_info_to_close.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_lock,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Secret key doesn\'t match specified secret lock.' == str(error.value)


def test_close_atomic_swap_before_approve():
    """
    Case: close swap before it is approved.
    Expect: invalid transaction error is raised with transaction cannot be closed before it is approved error message.
    """
    atomic_swap_close_payload = AtomicSwapClosePayload(
        swap_id=SWAP_ID,
        secret_key=SECRET_KEY,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.CLOSE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info_to_close = AtomicSwapInfo()
    existing_swap_info_to_close.swap_id = SWAP_ID
    existing_swap_info_to_close.state = AtomicSwapInfo.OPENED
    existing_swap_info_to_close.secret_lock = SECRET_LOCK
    existing_swap_info_to_close.is_initiator = True
    serialized_existing_swap_info_to_lock = existing_swap_info_to_close.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_lock,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Transaction cannot be closed before it\'s approved.' == str(error.value)
