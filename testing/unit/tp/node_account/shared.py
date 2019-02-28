from sawtooth_sdk.protobuf.setting_pb2 import Setting

from testing.mocks.stub import StubContext
from remme.tp.node_account import NodeAccountHandler, NodeAccount

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'


NODE_ACCOUNT_ADDRESS_FROM = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'
MINIMUM_STAKE_SETTINGS_ADDRESS = '0000007ca83d6bbb759da9cde0fb0dec1400c54773f137ea7cfe91e3b0c44298fc1c14'

NODE_ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

INPUTS = OUTPUTS = [
    NODE_ACCOUNT_ADDRESS_FROM,
    MINIMUM_STAKE_SETTINGS_ADDRESS,
]

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': NodeAccountHandler().family_name,
    'family_version': NodeAccountHandler().family_versions[0],
}


def create_context(account_from_balance, node_state=NodeAccount.NEW, frozen=0, unfrozen=0):
    """
    Create stub context with initial data.

    Stub context is an interface around Sawtooth state, consider as database.
    State is key-value storage that contains address with its data (i.e. account balance).

    References:
        - https://github.com/Remmeauth/remme-core/blob/dev/testing/mocks/stub.py
    """
    node_account = NodeAccount()

    node_account.balance = account_from_balance
    node_account.node_state = node_state
    node_account.reputation.frozen = frozen
    node_account.reputation.unfrozen = unfrozen
    serialized_account_from_balance = node_account.SerializeToString()


    initial_state = {
        NODE_ACCOUNT_ADDRESS_FROM: serialized_account_from_balance,
    }

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
