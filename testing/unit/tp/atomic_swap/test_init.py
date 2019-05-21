"""
Provide tests for atomic swap handler initialization method implementation.
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
from testing.utils.client import proto_error_msg
from remme.clients.block_info import (
    CONFIG_ADDRESS,
    BlockInfoClient,
)
from remme.protos.account_pb2 import Account
from remme.protos.atomic_swap_pb2 import (
    AtomicSwapInfo,
    AtomicSwapInitPayload,
    AtomicSwapMethod,
)
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512, client_to_real_amount
from remme.settings import (
    SETTINGS_KEY_ZERO_ADDRESS_OWNERS,
    ZERO_ADDRESS,
)
from remme.settings import TRANSACTION_FEE
from remme.settings.helper import _make_settings_key
from remme.tp.consensus_account import ConsensusAccountHandler, ConsensusAccount
from remme.tp.atomic_swap import AtomicSwapHandler
from remme.tp.basic import BasicHandler

TOKENS_AMOUNT_TO_SWAP = 200

BOT_ETHEREUM_ADDRESS = '0xe6ca0e7c974f06471759e9a05d18b538c5ced11e'
BOT_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
BOT_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'
BOT_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'

ALICE_ETHEREUM_ADDRESS = '0x8dfe0f55a1cf9b22b8c85a9ff7a85a28a3879f71'
ALICE_ADDRESS = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'
ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR = '0x6f4d5666332f5a575a714d4245624455612f2b4345424f704b4256704f5'

BOT_IT_IS_INITIATOR_MARK = ''
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

CURRENT_TIMESTAMP = int(datetime.datetime.now().timestamp())

BLOCK_INFO_CONFIG_ADDRESS = CONFIG_ADDRESS
BLOCK_INFO_ADDRESS = BlockInfoClient.create_block_address(1000)

block_info_config = BlockInfoConfig()
block_info_config.latest_block = 1000
SERIALIZED_BLOCK_INFO_CONFIG = block_info_config.SerializeToString()

block_info = BlockInfo()
block_info.timestamp = CURRENT_TIMESTAMP
SERIALIZED_BLOCK_INFO = block_info.SerializeToString()

INPUTS = [
    BLOCK_INFO_CONFIG_ADDRESS,
    BLOCK_INFO_ADDRESS,
    BOT_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
    ADDRESS_TO_STORE_SWAP_INFO_BY,
    ZERO_ADDRESS,
]

OUTPUTS = [
    ADDRESS_TO_STORE_SWAP_INFO_BY,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
    BOT_ADDRESS,
    ZERO_ADDRESS,
]


def test_atomic_swap_init_with_empty_proto():
    """
    Case: send empty proto for init
    Expect: invalid transaction error
    """
    inputs = outputs = [
        BLOCK_INFO_CONFIG_ADDRESS,
        BLOCK_INFO_ADDRESS,
        BOT_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY,
    ]

    atomic_swap_init_payload = AtomicSwapInitPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
    transaction_payload.data = atomic_swap_init_payload.SerializeToString()

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

    mock_context = StubContext(inputs=inputs, outputs=outputs, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        AtomicSwapInitPayload,
        {
            'receiver_address': ['Missed address.'],
            'sender_address_non_local': ['This field is required.'],
            'amount': ['This field is required.'],
            'swap_id': ['Missed swap_id.'],
        }
    ) == str(error.value)


def test_atomic_swap_init():
    """
    Case: initialize swap of bot's Remme node tokens to Alice's ERC20 Remme tokens.
    Expect: bot sends commission to the zero account address, swap amount is decreased from bot account.
    """

    atomic_swap_init_payload = AtomicSwapInitPayload(
        receiver_address=ALICE_ADDRESS,
        sender_address_non_local=BOT_ETHEREUM_ADDRESS,
        amount=TOKENS_AMOUNT_TO_SWAP,
        swap_id=SWAP_ID,
        secret_lock_by_solicitor=BOT_IT_IS_INITIATOR_MARK,
        email_address_encrypted_by_initiator=ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
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

    zero_account = Account()
    zero_account.balance = 0
    serialized_zero_account = zero_account.SerializeToString()

    bot_account = Account()
    bot_account.balance = client_to_real_amount(5000 + TRANSACTION_FEE)
    serialized_bot_account = bot_account.SerializeToString()

    consensus_account = ConsensusAccount()
    consensus_account.block_cost = 0
    serialized_consensus_account = consensus_account.SerializeToString()

    genesis_members_setting = Setting()
    genesis_members_setting.entries.add(key=SETTINGS_KEY_ZERO_ADDRESS_OWNERS, value=f'{BOT_PUBLIC_KEY},')
    serialized_genesis_members_setting = genesis_members_setting.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
        BOT_ADDRESS: serialized_bot_account,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
        ADDRESS_TO_GET_GENESIS_MEMBERS_AS_STRING_BY: serialized_genesis_members_setting,
        ZERO_ADDRESS: serialized_zero_account,
    })

    swap_info = AtomicSwapInfo()
    swap_info.swap_id = SWAP_ID
    swap_info.state = AtomicSwapInfo.OPENED
    swap_info.amount = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    swap_info.created_at = CURRENT_TIMESTAMP
    swap_info.email_address_encrypted_optional = ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR
    swap_info.sender_address = BOT_ADDRESS
    swap_info.sender_address_non_local = BOT_ETHEREUM_ADDRESS
    swap_info.receiver_address = ALICE_ADDRESS
    swap_info.is_initiator = True
    serialized_swap_info = swap_info.SerializeToString()

    expected_zero_account = Account()
    expected_zero_account.balance = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    serialized_expected_zero_account = expected_zero_account.SerializeToString()

    expected_bot_account = Account()
    expected_bot_account.balance = client_to_real_amount(5000 - TOKENS_AMOUNT_TO_SWAP)
    serialized_expected_bot_account = expected_bot_account.SerializeToString()

    expected_consensus_account = ConsensusAccount()
    expected_consensus_account.block_cost = client_to_real_amount(TRANSACTION_FEE)
    serialized_expected_consensus_account = expected_consensus_account.SerializeToString()

    expected_state = {
        BOT_ADDRESS: serialized_expected_bot_account,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_expected_consensus_account,
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_swap_info,
        ZERO_ADDRESS: serialized_expected_zero_account,
    }

    AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        BOT_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
        ZERO_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_atomic_swap_init_already_taken_id():
    """
    Case: initialize swap of bot's Remme node tokens to Alice's ERC20 Remme tokens with already existing swap id.
    Expect: invalid transaction error is raised with atomic swap id has already been taken error message.
    """

    atomic_swap_init_payload = AtomicSwapInitPayload(
        receiver_address=ALICE_ADDRESS,
        sender_address_non_local=BOT_ETHEREUM_ADDRESS,
        amount=TOKENS_AMOUNT_TO_SWAP,
        swap_id=SWAP_ID,
        secret_lock_by_solicitor=BOT_IT_IS_INITIATOR_MARK,
        email_address_encrypted_by_initiator=ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
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

    swap_info = AtomicSwapInfo()
    swap_info.swap_id = SWAP_ID
    swap_info.state = AtomicSwapInfo.OPENED
    swap_info.amount = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    swap_info.created_at = CURRENT_TIMESTAMP
    swap_info.email_address_encrypted_optional = ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR
    swap_info.sender_address = BOT_ADDRESS
    swap_info.sender_address_non_local = BOT_ETHEREUM_ADDRESS
    swap_info.receiver_address = ALICE_ADDRESS
    serialized_swap_info = swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Atomic swap ID has already been taken, please use a different one.' == str(error.value)


def test_atomic_swap_init_swap_no_block_config_info():
    """
    Case: initialize swap of bot's Remme node tokens to Alice's ERC20 Remme tokens when no block config settings.
    Expect: invalid transaction error is raised with nlock config not found error message.
    """

    atomic_swap_init_payload = AtomicSwapInitPayload(
        receiver_address=ALICE_ADDRESS,
        sender_address_non_local=BOT_ETHEREUM_ADDRESS,
        amount=TOKENS_AMOUNT_TO_SWAP,
        swap_id=SWAP_ID,
        secret_lock_by_solicitor=BOT_IT_IS_INITIATOR_MARK,
        email_address_encrypted_by_initiator=ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
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

    assert 'Block config not found.' == str(error.value)


def test_atomic_swap_init_swap_no_block_info():
    """
    Case: initialize swap of bot's Remme node tokens to Alice's ERC20 Remme tokens when no needed block information.
    Expect: invalid transaction error is raised with nlock config not found error message.
    """

    atomic_swap_init_payload = AtomicSwapInitPayload(
        receiver_address=ALICE_ADDRESS,
        sender_address_non_local=BOT_ETHEREUM_ADDRESS,
        amount=TOKENS_AMOUNT_TO_SWAP,
        swap_id=SWAP_ID,
        secret_lock_by_solicitor=BOT_IT_IS_INITIATOR_MARK,
        email_address_encrypted_by_initiator=ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
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

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Block {block_info_config.latest_block + 1} not found.' == str(error.value)


def test_atomic_swap_init_swap_receiver_address_invalid_type():
    """
    Case: initialize swap of bot's Remme node tokens to Alice's ERC20 Remme tokens with invalid Alice node address.
    Expect: invalid transaction error is raised with atomic swap id has already been taken error message.
    """
    invalid_receiver_address = '112934y*(J#QJ3UH*PD(:9B&TYDB*I0b0a8edc4104ef28093ee30'

    atomic_swap_init_payload = AtomicSwapInitPayload(
        receiver_address=invalid_receiver_address,
        sender_address_non_local=BOT_ETHEREUM_ADDRESS,
        amount=TOKENS_AMOUNT_TO_SWAP,
        swap_id=SWAP_ID,
        secret_lock_by_solicitor=BOT_IT_IS_INITIATOR_MARK,
        email_address_encrypted_by_initiator=ALICE_EMAIL_ADDRESS_ENCRYPTED_BY_INITIATOR,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.INIT
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

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        AtomicSwapInitPayload,
        {'receiver_address': ['Address is not of a blockchain token type.']}
    ) == str(error.value)
