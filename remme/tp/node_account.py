import logging
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.node_account_pb2 import (
    NodeAccount, NodeAccountMethod, NodeAccountInternalTransferPayload
)

from remme.protos.transaction_pb2 import (
    TransactionPayload
)

from remme.settings import (
    GENESIS_ADDRESS, ZERO_ADDRESS,
)
from remme.shared.forms import TransferPayloadForm, GenesisPayloadForm
from remme.shared.constants import Events, EMIT_EVENT

from .basic import (
    PB_CLASS, PROCESSOR, VALIDATOR, BasicHandler, get_data, get_multiple_data
)

from .account import get_account_by_address


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
                PB_CLASS: TransactionPayload,
                PROCESSOR: self._initialize_masternode,
               # VALIDATOR: TransferPayloadForm,
            },
            NodeAccountMethod.CLOSE_MASTERNODE: {
                PROCESSOR: self._close_masternode,
            },
            NodeAccountMethod.TRANSFER_FROM_UNFROZEN_TO_OPERATIONAL: {
                PB_CLASS: TransactionPayload,
                PROCESSOR: self._transfer_from_unfrozen_to_operational,
            }
        }

    def _initialize_masternode(self, context, node_account_public_key, internal_transfer_payload):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        if node_account.is_masternode_closed is True:
            raise InvalidTransaction('Masternode is already closed')

        if node_account.is_masternode is True:
            raise InvalidTransaction('Node is already a masternode')

        if internal_transfer_payload.amount < remme.settings.minimum_stake:
            raise InvalidTransaction('Initial stake is too low')

        node_account.is_masternode = True

        node_account.balance -= internal_transfer_payload.value
        frozen_part = remme.settings.minimum_stake
        unfrozen_part = internal_transfer_payload.value - remme.settings.minimum_stake
        node_account.reputational.frozen += frozen_part
        node_account.reputational.unfrozen += unfrozen_part

    def _close_masternode(self, context, node_account_public_key):
        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        if node_account.is_masternode_closed is True:
            raise InvalidTransaction('Masternode is already closed')

        if node_account.is_masternode is False:
            raise InvalidTransaction('Node is not masternode')

        node_account.is_masternode_closed = True
        node_account.is_masternode = False

        node_account.balance += node_account.reputational.frozen
        node_account.balance += node_account.reputational.unfrozen

        node_account.reputational.frozen = 0
        node_account.reputational.unfrozen = 0

    def _transfer_from_unfrozen_to_operational(self, context, node_account_public_key, internal_transfer_payload):

        node_account_address = self.make_address_from_data(node_account_public_key)

        node_account = get_node_account_by_address(context, node_account_address)

        node_account.reputational.unfrozen -= internal_transfer_payload.value
        node_account.balance += internal_transfer_payload.value
