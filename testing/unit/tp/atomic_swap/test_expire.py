"""
Provide tests for atomic swap handler expire method implementation.
"""
import datetime
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
from remme.protos.atomic_swap_pb2 import (
    AtomicSwapExpirePayload,
    AtomicSwapInfo,
    AtomicSwapMethod,
)
from remme.clients.block_info import (
    CONFIG_ADDRESS,
    BlockInfo,
    BlockInfoConfig,
    BlockInfoClient,
)
from remme.protos.account_pb2 import Account
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings.helper import _make_settings_key
from remme.shared.utils import hash512, web3_hash
from remme.tp.atomic_swap import AtomicSwapHandler
from remme.tp.basic import BasicHandler

from remme.settings import (
    SETTINGS_KEY_GENESIS_OWNERS,
    ZERO_ADDRESS,
)

TOKENS_AMOUNT_TO_SWAP = 200

BOT_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'
BOT_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
BOT_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'

ALICE_PRIVATE_KEY = '8c87d914a6cfeaf027413760ad359b5a56bfe0eda504d879b21872c7dc5b911c'
ALICE_PUBLIC_KEY = '02feb988591c78e58e57cdce5a314bd04798971227fcc2316907355392a2c99c25'
ALICE_ADDRESS = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'

SECRET_KEY = '3e0b064c97247732a3b345ce7b2a835d928623cb2871c26db4c2539a38e61a16'
SECRET_LOCK = web3_hash(SECRET_KEY)

SWAP_ID = '033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3884'

ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY = _make_settings_key(SETTINGS_KEY_GENESIS_OWNERS)
ADDRESS_TO_STORE_SWAP_INFO_BY = BasicHandler(
    name=AtomicSwapHandler().family_name, versions=AtomicSwapHandler()._family_versions[0]
).make_address_from_data(data=SWAP_ID)


TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': AtomicSwapHandler().family_name,
    'family_version': AtomicSwapHandler()._family_versions[0],
}

CURRENT_TIMESTAMP = int(datetime.datetime.now().timestamp())

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
RANDOM_PUBLIC_KEY = '8c87d914a6cfeaf027413760ad359b5a56bfe0eda504d879b21872c7dc5b911c'
RANDOM_ADDRESS = '1120077212221be0a8723c9d9070a047f0623e2933b30666a251523b071735573a099c'

BLOCK_INFO_CONFIG_ADDRESS = CONFIG_ADDRESS
BLOCK_INFO_ADDRESS = BlockInfoClient.create_block_address(1000)

block_info_config = BlockInfoConfig()
block_info_config.latest_block = 1000
SERIALIZED_BLOCK_INFO_CONFIG = block_info_config.SerializeToString()

block_info = BlockInfo()
block_info.timestamp = CURRENT_TIMESTAMP
SERIALIZED_BLOCK_INFO = block_info.SerializeToString()

INPUTS = OUTPUTS = [
    ADDRESS_TO_STORE_SWAP_INFO_BY,
]


def test_expire_atomic_swap():
    """
    Case: to expire atomic swap.
    Expect: transfer (without commission back) atomic swap amount from zero address to the bot address back.
    """
    inputs = outputs = [
        BLOCK_INFO_CONFIG_ADDRESS,
        BLOCK_INFO_ADDRESS,
        BOT_ADDRESS,
        ZERO_ADDRESS,
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY,
    ]

    atomic_swap_expire_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.EXPIRE
    transaction_payload.data = atomic_swap_expire_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    bot_account = Account()
    bot_account.balance = 4700
    serialized_bot_account = bot_account.SerializeToString()

    zero_account = Account()
    zero_account.balance = 300
    serialized_zero_account = zero_account.SerializeToString()

    genesis_members_setting = Setting()
    genesis_members_setting.entries.add(key=SETTINGS_KEY_GENESIS_OWNERS, value=f'{BOT_PUBLIC_KEY},')
    serialized_genesis_members_setting = genesis_members_setting.SerializeToString()

    existing_swap_info = AtomicSwapInfo()
    existing_swap_info.swap_id = SWAP_ID
    existing_swap_info.state = AtomicSwapInfo.OPENED
    existing_swap_info.amount = TOKENS_AMOUNT_TO_SWAP
    existing_swap_info.created_at = CURRENT_TIMESTAMP // 2
    existing_swap_info.sender_address = BOT_ADDRESS
    existing_swap_info.receiver_address = ALICE_ADDRESS
    existing_swap_info.is_initiator = True
    serialized_existing_swap_info = existing_swap_info.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
        BOT_ADDRESS: serialized_bot_account,
        ZERO_ADDRESS: serialized_zero_account,
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY: serialized_genesis_members_setting,
    })

    expected_bot_account = Account()
    expected_bot_account.balance = 4700 + TOKENS_AMOUNT_TO_SWAP
    serialized_expected_bot_account = expected_bot_account.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = 300 - TOKENS_AMOUNT_TO_SWAP
    serialized_expected_zero_account = expected_zero_account.SerializeToString()

    expected_swap_info = AtomicSwapInfo()
    expected_swap_info.swap_id = SWAP_ID
    expected_swap_info.state = AtomicSwapInfo.EXPIRED
    expected_swap_info.amount = TOKENS_AMOUNT_TO_SWAP
    expected_swap_info.created_at = CURRENT_TIMESTAMP // 2
    expected_swap_info.sender_address = BOT_ADDRESS
    expected_swap_info.receiver_address = ALICE_ADDRESS
    expected_swap_info.is_initiator = True
    serialized_expected_swap_info = expected_swap_info.SerializeToString()

    expected_state = {
        BOT_ADDRESS: serialized_expected_bot_account,
        ZERO_ADDRESS: serialized_expected_zero_account,
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_expected_swap_info,
    }

    AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ADDRESS_TO_STORE_SWAP_INFO_BY, BOT_ADDRESS, ZERO_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_expire_not_initialized_atomic_swap():
    """
    Case: to expire not initialized atomic swap.
    Expect: invalid transaction error is raised with atomic swap was not initiated error message.
    """
    atomic_swap_close_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
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


def test_expire_already_closed_atomic_swap():
    """
    Case: to expire already closed atomic swap.
    Expect: invalid transaction error is raised with already operation with closed or expired swap error message.
    """
    atomic_swap_close_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
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


def test_expire_atomic_swap_by_not_swap_owner():
    """
    Case: to expire atomic swap by signer address isn't specified in atomic swap sender address.
    Expect: invalid transaction error is raised with signer is not the one who opened the swap. error message.
    """
    inputs = outputs = [
        BOT_ADDRESS,
        ZERO_ADDRESS,
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY,
    ]

    atomic_swap_close_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.EXPIRE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info_to_expire = AtomicSwapInfo()
    existing_swap_info_to_expire.swap_id = SWAP_ID
    existing_swap_info_to_expire.state = AtomicSwapInfo.OPENED
    existing_swap_info_to_expire.sender_address = RANDOM_ADDRESS
    serialized_existing_swap_info_to_expire = existing_swap_info_to_expire.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_expire,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Signer is not the one who opened the swap.' == str(error.value)


def test_expire_atomic_swap_before_invalid_withdrawal_by_alice():
    """
    Case: to expire atomic swap by alice if 24 hasn't been passed from atomic swap initialization timestamp.
    Expect: invalid transaction error is raised with signer is not the one who opened the swap. error message.
    """
    inputs = outputs = [
        BLOCK_INFO_CONFIG_ADDRESS,
        BLOCK_INFO_ADDRESS,
        BOT_ADDRESS,
        ZERO_ADDRESS,
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY,
    ]

    atomic_swap_close_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.EXPIRE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=ALICE_PUBLIC_KEY,
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
        signature=create_signer(private_key=ALICE_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context_for_blocks = StubContext(inputs=inputs, outputs=outputs, initial_state={
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
    })

    current_timestamp = AtomicSwapHandler()._get_latest_block_info(mock_context_for_blocks).timestamp

    existing_swap_info_to_expire = AtomicSwapInfo()
    existing_swap_info_to_expire.swap_id = SWAP_ID
    existing_swap_info_to_expire.state = AtomicSwapInfo.OPENED
    existing_swap_info_to_expire.sender_address = ALICE_ADDRESS
    existing_swap_info_to_expire.created_at = current_timestamp
    existing_swap_info_to_expire.is_initiator = False
    serialized_existing_swap_info_to_expire = existing_swap_info_to_expire.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_expire,
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Swap non initiator needs to wait 48 hours since timestamp {current_timestamp} to withdraw.' == \
           str(error.value)


def test_expire_atomic_swap_before_invalid_withdrawal_by_bot():
    """
    Case: to expire atomic swap by bot if 48 hasn't been passed from atomic swap initialization timestamp.
    Expect: invalid transaction error is raised with signer is not the one who opened the swap. error message.
    """
    inputs = outputs = [
        BLOCK_INFO_CONFIG_ADDRESS,
        BLOCK_INFO_ADDRESS,
        BOT_ADDRESS,
        ZERO_ADDRESS,
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY,
    ]

    atomic_swap_close_payload = AtomicSwapExpirePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.EXPIRE
    transaction_payload.data = atomic_swap_close_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
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
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info_to_expire = AtomicSwapInfo()
    existing_swap_info_to_expire.swap_id = SWAP_ID
    existing_swap_info_to_expire.state = AtomicSwapInfo.OPENED
    existing_swap_info_to_expire.sender_address = BOT_ADDRESS
    existing_swap_info_to_expire.created_at = CURRENT_TIMESTAMP
    existing_swap_info_to_expire.is_initiator = True
    serialized_existing_swap_info_to_expire = existing_swap_info_to_expire.SerializeToString()

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info_to_expire,
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Swap initiator needs to wait 24 hours since timestamp {CURRENT_TIMESTAMP} to withdraw.' == \
           str(error.value)
