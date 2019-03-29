from sawtooth_sdk.protobuf.setting_pb2 import Setting

from remme.protos.node_account_pb2 import NodeAccount
from remme.tp.obligatory_payment import ObligatoryPaymentHandler
from testing.mocks.stub import StubContext

from remme.settings import (
    CONSENSUS_ALLOWED_VALIDATORS,
    SETTINGS_OBLIGATORY_PAYMENT,
    SETTINGS_COMMITTEE_SIZE,
)

from remme.settings.helper import _make_settings_key

COMMITTEE_SIZE = 10
OBLIGATORY_PAYMENT = 1

BLOCK_WINNER_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
COMMITTEE_PUBLIC_KEYS = []
for i in range(0, COMMITTEE_SIZE):
    COMMITTEE_PUBLIC_KEYS.append(
        (str(hex(int(BLOCK_WINNER_PUBLIC_KEY, 16) + i))[2:]).rjust(66, '0')
    )
BLOCK_WINNER_ADDRESS = '5f15bcd71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'

COMMITTEE_ADDRESSES = []
for i in range(0, COMMITTEE_SIZE):
    COMMITTEE_ADDRESSES.append(
        ObligatoryPaymentHandler().make_address_from_data(COMMITTEE_PUBLIC_KEYS[i])
    )

BLOCK_WINNER_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

ADDRESS_TO_GET_ALLOWED_VALIDATORS = _make_settings_key(CONSENSUS_ALLOWED_VALIDATORS)
ADDRESS_TO_GET_OBLIGATORY_PAYMENT = _make_settings_key(SETTINGS_OBLIGATORY_PAYMENT)
ADDRESS_TO_GET_COMMITTEE_SIZE = _make_settings_key(SETTINGS_COMMITTEE_SIZE)

INPUTS = OUTPUTS = [
    ADDRESS_TO_GET_ALLOWED_VALIDATORS,
    ADDRESS_TO_GET_OBLIGATORY_PAYMENT,
    ADDRESS_TO_GET_COMMITTEE_SIZE,
]
INPUTS.extend(COMMITTEE_ADDRESSES)
OUTPUTS.extend(COMMITTEE_ADDRESSES)

TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': ObligatoryPaymentHandler().family_name,
    'family_version': ObligatoryPaymentHandler().family_versions[0],
}


def create_context(operational_balance, frozen_balance, unfrozen_balance, allowed_validators=None):
    """
    Create stub context with initial data.

    Stub context is an interface around Sawtooth state, consider as database.
    State is key-value storage that contains address with its data (i.e. account balance).

    References:
        - https://github.com/Remmeauth/remme-core/blob/dev/testing/mocks/stub.py
    """
    serialized_node_accounts = []
    for i in range(0, COMMITTEE_SIZE):
        node_account = NodeAccount()

        node_account.balance = operational_balance
        node_account.node_state = NodeAccount.OPENED
        node_account.reputation.frozen = frozen_balance
        node_account.reputation.unfrozen = unfrozen_balance
        serialized_node_account = node_account.SerializeToString()

        serialized_node_accounts.append(serialized_node_account)

    obligatory_payment_settings = Setting()
    if allowed_validators is None:
        allowed_validators = ';'.join(COMMITTEE_PUBLIC_KEYS)
    obligatory_payment_settings.entries.add(key=CONSENSUS_ALLOWED_VALIDATORS, value=allowed_validators)
    obligatory_payment_settings.entries.add(key=SETTINGS_OBLIGATORY_PAYMENT, value=str(OBLIGATORY_PAYMENT))
    obligatory_payment_settings.entries.add(key=SETTINGS_COMMITTEE_SIZE, value=str(COMMITTEE_SIZE))
    serialized_obligatory_payment_setting = obligatory_payment_settings.SerializeToString()

    initial_state = {
        ADDRESS_TO_GET_ALLOWED_VALIDATORS: serialized_obligatory_payment_setting,
        ADDRESS_TO_GET_OBLIGATORY_PAYMENT: serialized_obligatory_payment_setting,
        ADDRESS_TO_GET_COMMITTEE_SIZE: serialized_obligatory_payment_setting,
    }

    for i in range(0, COMMITTEE_SIZE):
        initial_state[COMMITTEE_ADDRESSES[i]] = serialized_node_accounts[i]

    return StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
