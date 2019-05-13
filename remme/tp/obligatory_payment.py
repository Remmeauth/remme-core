# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
import logging
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.obligatory_payment_pb2 import (
    ObligatoryPaymentPayload,
    ObligatoryPaymentMethod
)

from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeState,
)
from remme.settings import (
    SETTINGS_OBLIGATORY_PAYMENT,
    NODE_STATE_ADDRESS,
)
from remme.tp.node_account import NodeAccountHandler
from remme.protos.consensus_account_pb2 import ConsensusAccount

from remme.shared.forms import (
    ObligatoryPaymentPayloadForm,
)
from remme.shared.utils import hash512, client_to_real_amount, real_to_client_amount
from remme.settings.helper import _get_setting_value

from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    FEE_AUTO_CHARGER,
    BasicHandler,
    get_data,
    get_multiple_data
)
from .consensus_account import ConsensusAccountHandler


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'obligatory_payment'
FAMILY_VERSIONS = ['0.1']


class ObligatoryPaymentHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT: {
                PB_CLASS: ObligatoryPaymentPayload,
                PROCESSOR: self._pay_obligatory_payment,
                VALIDATOR: ObligatoryPaymentPayloadForm,
                FEE_AUTO_CHARGER: None,
            },
        }

    def __withdraw_obligatory_payment(self, node_account, obligatory_payment):
        if node_account.balance >= obligatory_payment:
            node_account.balance -= obligatory_payment

        elif node_account.reputation.unfrozen >= obligatory_payment:
            node_account.reputation.unfrozen -= obligatory_payment

        elif node_account.reputation.frozen >= obligatory_payment:
            node_account.reputation.frozen -= obligatory_payment

        else:
            raise InvalidTransaction("Malformed committee. A node doesn't have enough tokens to pay obligatory payment.")

    def __get_obligatory_payment_parameters(self, context):
        node_state = get_data(context, NodeState, NODE_STATE_ADDRESS)
        committee_pub_keys = node_state.master_nodes
        committee_size = len(committee_pub_keys)
        if committee_size == 0:
            raise InvalidTransaction('Committee size should be a positive integer.')
        obligatory_payment = _get_setting_value(context, SETTINGS_OBLIGATORY_PAYMENT)
        try:
            obligatory_payment = client_to_real_amount(int(obligatory_payment))
        except e:
            raise InvalidTransaction('Obligatory payment amount should be a positive integer.')
        if obligatory_payment == 0:
            raise InvalidTransaction('Obligatory payment amount should be a positive integer.')

        return committee_pub_keys, obligatory_payment, committee_size

    def _pay_obligatory_payment(self, context, node_account_public_key, obligatory_payment_payload):
        node_account_address = NodeAccountHandler().make_address_from_data(node_account_public_key)
        node_account = get_data(context, NodeAccount, node_account_address)
        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        consensus_account = get_data(context, ConsensusAccount, ConsensusAccountHandler.CONSENSUS_ADDRESS)
        if consensus_account is None:
            raise InvalidTransaction('Consensus account not found')

        committee_addresses, obligatory_payment, committee_size = self.__get_obligatory_payment_parameters(context)

        state = {
            node_account_address: node_account,
            ConsensusAccountHandler.CONSENSUS_ADDRESS: consensus_account,
        }
        try:
            committee_addresses.remove(node_account_address)  # committee to charge obligatory payment
        except ValueError:
            pass

        committee_node_accounts = get_multiple_data(context, [
            (address, NodeAccount) for address in committee_addresses
        ])
        for i, committee_node_account in enumerate(committee_node_accounts):
            if committee_node_account is None:
                raise InvalidTransaction('Invalid context or address.')

            address = committee_addresses[i]

            self.__withdraw_obligatory_payment(committee_node_account, obligatory_payment)
            state[address] = committee_node_account

        payment = client_to_real_amount((committee_size - 1) * obligatory_payment, 0)

        consensus_account.obligatory_payments += payment

        LOGGER.info(f"Obligatory payment total: {real_to_client_amount(payment)}")

        return state
