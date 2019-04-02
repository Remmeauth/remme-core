from sawtooth_sdk.protobuf.setting_pb2 import Setting

from testing.mocks.stub import StubContext
from remme.tp.account import Account
from remme.tp.node_account import NodeAccountHandler, NodeAccount
from remme.tp.consensus_account import ConsensusAccountHandler, ConsensusAccount

from remme.settings import SETTINGS_MINIMUM_STAKE, NODE_STATE_ADDRESS, ZERO_ADDRESS, SETTINGS_GENESIS_OWNERS
from remme.settings.helper import _make_settings_key

from remme.shared.utils import client_to_real_amount

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

MINIMUM_STAKE = 250000

NODE_ACCOUNT_ADDRESS_FROM = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
MINIMUM_STAKE_SETTINGS_ADDRESS = '0000007ca83d6bbb759da9cde0fb0dec1400c54773f137ea7cfe91e3b0c44298fc1c14'

NODE_ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

ADDRESS_TO_GET_MINIMUM_STAKE = _make_settings_key(SETTINGS_MINIMUM_STAKE)
ADDRESS_GENESIS_OWNERS = _make_settings_key(SETTINGS_GENESIS_OWNERS)

INPUTS = OUTPUTS = [
    NODE_ACCOUNT_ADDRESS_FROM,
    ADDRESS_TO_GET_MINIMUM_STAKE,
    NODE_STATE_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
    ZERO_ADDRESS,
    ADDRESS_GENESIS_OWNERS,
]

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': NodeAccountHandler().family_name,
    'family_version': NodeAccountHandler().family_versions[0],
}

BLOCK_COST = 100


def create_context(account_from_balance, node_state=NodeAccount.NEW, frozen=0, unfrozen=0,
                   fixed_amount=0, min=False, max=False, block_cost=BLOCK_COST,
                   min_stake=MINIMUM_STAKE):
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
    if fixed_amount:
        node_account.fixed_amount = fixed_amount
    elif min:
        node_account.min = min
    elif max:
        node_account.max = max
    else:
        # default
        node_account.min = True
    serialized_account_from_balance = node_account.SerializeToString()

    swap_commission_setting = Setting()
    swap_commission_setting.entries.add(key=SETTINGS_MINIMUM_STAKE, value=str(min_stake))
    serialized_swap_commission_setting = swap_commission_setting.SerializeToString()

    genesis_owners_setting = Setting()
    genesis_owners_setting.entries.add(key=SETTINGS_GENESIS_OWNERS, value='')
    serialized_genesis_owners_setting = genesis_owners_setting.SerializeToString()

    consensus_account = ConsensusAccount()
    # TODO: Uncomment in the future
    # consensus_account.block_cost = block_cost
    serialized_consensus_account = consensus_account.SerializeToString()

    initial_state = {
        NODE_ACCOUNT_ADDRESS_FROM: serialized_account_from_balance,
        ADDRESS_TO_GET_MINIMUM_STAKE: serialized_swap_commission_setting,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
        ZERO_ADDRESS: Account(balance=client_to_real_amount(block_cost)).SerializeToString(),
        ADDRESS_GENESIS_OWNERS: serialized_genesis_owners_setting,
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
