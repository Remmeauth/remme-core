import datetime

from sawtooth_sdk.protobuf.setting_pb2 import Setting

from testing.mocks.stub import StubContext
from remme.tp.consensus_account import ConsensusAccount, ConsensusAccountHandler
from remme.tp.node_account import NodeAccount
from remme.tp.account import Account

from remme.shared.utils import client_to_real_amount
from remme.settings import (
    SETTINGS_MINIMUM_STAKE,
    SETTINGS_BLOCKCHAIN_TAX,
    SETTINGS_MIN_SHARE,
    ZERO_ADDRESS,
)
from remme.settings.helper import _make_settings_key
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.clients.block_info import (
    CONFIG_ADDRESS,
    BlockInfoClient,
)

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

MINIMUM_STAKE = 250000

GENESIS_ACCOUNT_ADDRESS = '112007d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
NODE_ACCOUNT_SIGNER_ADDRESS = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
NODE_ACCOUNT_SIGNER_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

MINIMUM_STAKE_ADDRESS = _make_settings_key(SETTINGS_MINIMUM_STAKE)
BLOCKCHAIN_TAX_ADDRESS = _make_settings_key(SETTINGS_BLOCKCHAIN_TAX)
MIN_SHARE_ADDRESS = _make_settings_key(SETTINGS_MIN_SHARE)

CURRENT_TIMESTAMP = int(datetime.datetime.now().timestamp())

BLOCK_INFO_CONFIG_ADDRESS = CONFIG_ADDRESS
BLOCK_INFO_ADDRESS = BlockInfoClient.create_block_address(1000)

block_info_config = BlockInfoConfig()
block_info_config.latest_block = 1000
SERIALIZED_BLOCK_INFO_CONFIG = block_info_config.SerializeToString()

block_info = BlockInfo()
block_info.timestamp = CURRENT_TIMESTAMP
block_info.block_num = 1000
block_info.signer_public_key = RANDOM_NODE_PUBLIC_KEY
SERIALIZED_BLOCK_INFO = block_info.SerializeToString()

INPUTS = OUTPUTS = [
    NODE_ACCOUNT_SIGNER_ADDRESS,
    MINIMUM_STAKE_ADDRESS,
    BLOCKCHAIN_TAX_ADDRESS,
    MIN_SHARE_ADDRESS,
    BLOCK_INFO_CONFIG_ADDRESS,
    BLOCK_INFO_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
    GENESIS_ACCOUNT_ADDRESS,
    ZERO_ADDRESS,
]

TRANSACTION_REQUEST_CONSENSUS_ACCOUNT_HANDLER_PARAMS = {
    'family_name': ConsensusAccountHandler().family_name,
    'family_version': ConsensusAccountHandler().family_versions[0],
}

OBLIGATORY_PAYMENTS = 100
BLOCK_COST = 20
BET_VALUE = 100


def create_context(account_from_balance=0, bet_value=BET_VALUE, node_state=NodeAccount.NEW, frozen=0, unfrozen=0,
                   obligatory_payments=OBLIGATORY_PAYMENTS, block_cost=BLOCK_COST):
    """
    Create stub context with initial data.

    Stub context is an interface around Sawtooth state, consider as database.
    State is key-value storage that contains address with its data (i.e. account balance).

    References:
        - https://github.com/Remmeauth/remme-core/blob/dev/testing/mocks/stub.py
    """
    node_account = NodeAccount()

    node_account.balance = client_to_real_amount(account_from_balance)
    node_account.node_state = node_state
    node_account.reputation.frozen = client_to_real_amount(frozen)
    node_account.reputation.unfrozen = client_to_real_amount(unfrozen)

    serialized_node_account = node_account.SerializeToString()

    min_stake_setting = Setting()
    min_stake_setting.entries.add(key=SETTINGS_MINIMUM_STAKE, value=str(250000))

    bc_tax_setting = Setting()
    bc_tax_setting.entries.add(key=SETTINGS_BLOCKCHAIN_TAX, value=str(0.1))

    min_share_setting = Setting()
    min_share_setting.entries.add(key=SETTINGS_MIN_SHARE, value=str(0.45))

    consensus_account = ConsensusAccount()
    consensus_account.public_key = RANDOM_NODE_PUBLIC_KEY
    consensus_account.obligatory_payments = client_to_real_amount(obligatory_payments)
    # TODO: Undo in the future
    # consensus_account.block_cost = block_cost
    consensus_account.bets[NODE_ACCOUNT_SIGNER_ADDRESS] = client_to_real_amount(bet_value)
    serialized_consensus_account = consensus_account.SerializeToString()

    initial_state = {
        NODE_ACCOUNT_SIGNER_ADDRESS: serialized_node_account,
        MINIMUM_STAKE_ADDRESS: min_stake_setting.SerializeToString(),
        BLOCKCHAIN_TAX_ADDRESS: bc_tax_setting.SerializeToString(),
        MIN_SHARE_ADDRESS: min_share_setting.SerializeToString(),
        BLOCK_INFO_CONFIG_ADDRESS: SERIALIZED_BLOCK_INFO_CONFIG,
        BLOCK_INFO_ADDRESS: SERIALIZED_BLOCK_INFO,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
        GENESIS_ACCOUNT_ADDRESS: Account(balance=0).SerializeToString(),
        ZERO_ADDRESS: Account(balance=client_to_real_amount(block_cost)).SerializeToString(),
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
