import logging
from sawtooth_sdk.processor.exceptions import InvalidTransaction


from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
    CloseMasternodePayload
)

from remme.shared.forms import (
    NodeAccountInternalTransferPayloadForm,
    CloseMasternodePayloadForm
)

from remme.settings import SETTINGS_MINIMUM_STAKE

from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)
from remme.settings.helper import _get_setting_value
LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'node_account'
FAMILY_VERSIONS = ['0.1']


class NodeAccountHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._transfer_from_unfrozen_to_operational,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.INITIALIZE_MASTERNODE: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._initialize_masternode,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.CLOSE_MASTERNODE: {
                PROCESSOR: self._close_masternode,
                PB_CLASS: CloseMasternodePayload,
                VALIDATOR: CloseMasternodePayloadForm,
            },
        }


    def _initialize_masternode(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            node_account = NodeAccount()

        if node_account.node_state != NodeAccount.NEW:
            raise InvalidTransaction('Masternode is already opened or closed.')

        if node_account.balance < internal_transfer_payload.value:
            raise InvalidTransaction('Insufficient amount of tokens on operational account.')

        minimum_stake = _get_setting_value(context, SETTINGS_MINIMUM_STAKE)
        if minimum_stake is None or not minimum_stake.isdigit():
            raise InvalidTransaction('remme.settings.minimum_stake is malformed. Should be not negative integer.')
        minimum_stake = int(minimum_stake)

        if internal_transfer_payload.value < minimum_stake:
            raise InvalidTransaction('Initial stake is too low.')

        node_account.node_state = NodeAccount.OPENED

        node_account.balance -= internal_transfer_payload.value

        unfrozen_part = internal_transfer_payload.value - minimum_stake
        node_account.reputation.frozen += minimum_stake
        node_account.reputation.unfrozen += unfrozen_part

        return {
            node_account_address: node_account,
        }

    def _close_masternode(self, context, node_account_public_key, payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.node_state != NodeAccount.OPENED:
            raise InvalidTransaction('Masternode is not opened or has been closed.')

        node_account.node_state = NodeAccount.CLOSED

        node_account.balance += node_account.reputation.frozen
        node_account.balance += node_account.reputation.unfrozen

        node_account.reputation.frozen = 0
        node_account.reputation.unfrozen = 0

        return {
            node_account_address: node_account,
        }

    def _transfer_from_unfrozen_to_operational(self, context, node_account_public_key, internal_transfer_payload):

        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        if node_account.reputation.unfrozen < internal_transfer_payload.value:
            raise InvalidTransaction('Insufficient amount of tokens on unfrozen account.')

        node_account.reputation.unfrozen -= internal_transfer_payload.value
        node_account.balance += internal_transfer_payload.value

        return {
            node_account_address: node_account,
        }
