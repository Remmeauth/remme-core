"""
Provide tests for node account calculate F(R) and Z(t) formulas implementation.
"""
import time
from decimal import Decimal
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
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.clients.block_info import (
    CONFIG_ADDRESS,
    BlockInfoClient,
)
from remme.settings import (
    SETTINGS_MINIMUM_STAKE,
    SETTINGS_SWAP_COMMISSION,
    SETTINGS_BLOCKCHAIN_TAX,
)
from remme.settings.helper import _make_settings_key
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler, get_latest_block, get_block_by_num, get_block_cost
from remme.tp.context import CacheContextService
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg
from .utils import get_node_blocks

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

FROZEN = 612_345
UNFROZEN = 100_000
MINIMUM_STAKE = 250_000
SWAP_COMMISSION_AMOUNT = 100
BLOCKCHAIN_TAX_AMOUNT = 0.1
MAX_REWARD_PCT = 0.9

NODE_ACCOUNT_ADDRESS_FROM = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'

NODE_ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT = _make_settings_key(SETTINGS_MINIMUM_STAKE)
ADDRESS_TO_GET_SWAP_COMMISSION_AMOUNT = _make_settings_key(SETTINGS_SWAP_COMMISSION)
ADDRESS_TO_GET_BLOCKCHAIN_TAX_AMOUNT = _make_settings_key(SETTINGS_BLOCKCHAIN_TAX)


blocks_address, initial_states = get_node_blocks(
    blocks_per_day=5,
    entropy=50,
    time_delta=300,
    node_account_public_key=RANDOM_NODE_PUBLIC_KEY)

INPUTS = OUTPUTS = [
    NODE_ACCOUNT_ADDRESS_FROM,
    ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT,
    ADDRESS_TO_GET_SWAP_COMMISSION_AMOUNT,
    ADDRESS_TO_GET_BLOCKCHAIN_TAX_AMOUNT,
]

INPUTS.extend(blocks_address)


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
        -
    """
    node_account = NodeAccount()

    node_account.reputation.frozen = account_from_frozen_balance
    node_account.reputation.unfrozen = account_to_unfrozen_balance
    serialized_account_balance = node_account.SerializeToString()

    minimum_stake_setting = Setting()
    minimum_stake_setting.entries.add(key=SETTINGS_MINIMUM_STAKE, value=str(minimum_stake))
    serialized_minimum_stake_setting = minimum_stake_setting.SerializeToString()

    swap_commission_setting = Setting()
    swap_commission_setting.entries.add(key=SETTINGS_SWAP_COMMISSION, value=str(SWAP_COMMISSION_AMOUNT))
    serialized_swap_commission_setting = swap_commission_setting.SerializeToString()

    blockchain_tax_setting = Setting()
    blockchain_tax_setting.entries.add(key=SETTINGS_BLOCKCHAIN_TAX, value=str(BLOCKCHAIN_TAX_AMOUNT))
    serialized_blockchain_tax_setting = blockchain_tax_setting.SerializeToString()

    initial_state = {
        NODE_ACCOUNT_ADDRESS_FROM: serialized_account_balance,
        ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT: serialized_minimum_stake_setting,
        ADDRESS_TO_GET_SWAP_COMMISSION_AMOUNT: serialized_swap_commission_setting,
        ADDRESS_TO_GET_BLOCKCHAIN_TAX_AMOUNT: serialized_blockchain_tax_setting,
    }
    initial_state.update(initial_states)

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)


def test_get_available_pct_distribution_reward():

    transaction_payload = TransactionPayload()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=NODE_ACCOUNT_ADDRESS_FROM,
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

    context_service = CacheContextService(context=mock_context)
    context_service.preload_state(INPUTS)

    pct_distribution_reward = NodeAccountHandler()._get_available_pct_distribution_reward(
        context_service,
        RANDOM_NODE_PUBLIC_KEY)

    assert pct_distribution_reward == Decimal('0.5224690')


def test_get_available_pct_distribution_reward_with_small_frozen_balance():

    node_frozen_balance = 230_000

    mock_context = create_context(account_from_frozen_balance=node_frozen_balance, account_to_unfrozen_balance=UNFROZEN)

    context_service = CacheContextService(context=mock_context)
    context_service.preload_state(INPUTS)

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler()._get_available_pct_distribution_reward(context_service, RANDOM_NODE_PUBLIC_KEY)

    assert str(error.value) == 'Frozen balance is lower than the minimum stake.'


def test_get_max_available_pct_distribution_reward():

    node_frozen_balance = 250_000 * 20

    mock_context = create_context(account_from_frozen_balance=node_frozen_balance, account_to_unfrozen_balance=UNFROZEN)

    context_service = CacheContextService(context=mock_context)
    context_service.preload_state(INPUTS)

    pct_distribution_reward = NodeAccountHandler()._get_available_pct_distribution_reward(
        context_service,
        RANDOM_NODE_PUBLIC_KEY)

    assert pct_distribution_reward == Decimal(str(MAX_REWARD_PCT))


def test_get_available_amount_defrosting_tokens_to_unfrozen():

    mock_context = create_context(account_from_frozen_balance=FROZEN, account_to_unfrozen_balance=UNFROZEN)

    context_service = CacheContextService(context=mock_context)
    context_service.preload_state(INPUTS)

    reward = NodeAccountHandler()._get_available_amount_defrosting_tokens_to_unfrozen(
        context_service,
        RANDOM_NODE_PUBLIC_KEY)

    assert reward == (536, 50)
