import logging
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.account_pb2 import AccountMethod
from remme.protos.node_account_pb2 import (
    NodeAccount, NodeAccountMethod, NodeAccountInternalTransferPayload,
)

from remme.shared.forms import NodeAccountInternalTransferPayloadForm
from remme.shared.constants import Events, EMIT_EVENT

from .basic import (
    PB_CLASS, PROCESSOR, VALIDATOR, BasicHandler, get_data, get_multiple_data
)
from remme.settings.helper import _get_setting_value
LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'node_account'
FAMILY_VERSIONS = ['0.1']


def get_node_account_by_address(context, address):
    account = get_data(context, NodeAccount, address)
    if account is None:
        return NodeAccount()
    return account


class NodeAccountHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            NodeAccountMethod.INITIALIZE_MASTERNODE: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._initialize_masternode,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            },
            NodeAccountMethod.CLOSE_MASTERNODE: {
                PROCESSOR: self._close_masternode,
            },
            NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL: {
                PB_CLASS: NodeAccountInternalTransferPayload,
                PROCESSOR: self._transfer_from_unfrozen_to_operational,
                VALIDATOR: NodeAccountInternalTransferPayloadForm,
            }
        }

    def _initialize_masternode(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        if node_account.node_state != NodeAccount.NodeState.Value('NEW'):
            raise InvalidTransaction('Masternode is already opened or closed')
        minimum_stake = 250000#_get_setting_value(context, 'minimum_stake')

        if internal_transfer_payload.value < minimum_stake:
            raise InvalidTransaction('Initial stake is too low')

        node_account.node_state = NodeAccount.NodeState.Value('OPENED')

        node_account.balance -= internal_transfer_payload.value
        frozen_part = minimum_stake
        unfrozen_part = internal_transfer_payload.value - minimum_stake
        node_account.reputation.frozen += frozen_part
        node_account.reputation.unfrozen += unfrozen_part

        return {
            node_account_address: node_account,
        }

    def _close_masternode(self, context, node_account_public_key):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        if node_account.node_state != NodeAccount.NodeState.Value('OPENED'):
            raise InvalidTransaction('Masternode is not opened or has been closed ')

        node_account.node_state = NodeAccount.NodeState.Value('CLOSED')

        node_account.balance += node_account.reputational.frozen
        node_account.balance += node_account.reputational.unfrozen

        node_account.reputational.frozen = 0
        node_account.reputational.unfrozen = 0

        return {
            node_account_address: node_account,
        }

    def _transfer_from_unfrozen_to_operational(self, context, node_account_public_key, internal_transfer_payload):

        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        node_account.reputational.unfrozen -= internal_transfer_payload.value
        node_account.balance += internal_transfer_payload.value

        return {
            node_account_address: node_account,
        }
