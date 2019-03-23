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

from remme.shared.forms import (
    ObligatoryPaymentPayloadForm,
)

from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)
from remme.shared.utils import hash512
from remme.settings.helper import _get_setting_value
LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'obligatory_payment'
FAMILY_VERSIONS = ['0.1']


def withdraw_obligatory_payment(node_account, obligatory_payment):
    if node_account.balance >= obligatory_payment:
        node_account.balance -= obligatory_payment

    elif node_account.reputation.unfrozen >= obligatory_payment:
        node_account.reputation.unfrozen -= obligatory_payment

    elif node_account.reputation.frozen >= obligatory_payment:
        node_account.reputation.frozen -= obligatory_payment

    else:
        raise InvalidTransaction("Malformed committee. A node doesn't have enough tokens to pay obligatory payment.")

def get_obligatory_payment_parameters(context):
    node_state = get_data(context, NodeState, NODE_STATE_ADDRESS)
    committee_pub_keys = node_state.master_nodes
    committee_size = len(committee_pub_keys)
    if committee_size == 0:
        raise InvalidTransaction('Committee size should be a positive integer.')
    obligatory_payment = _get_setting_value(context, SETTINGS_OBLIGATORY_PAYMENT)
    try:
        obligatory_payment = int(obligatory_payment)
    except e:
        raise InvalidTransaction('Obligatory payment amount should be a positive integer.')
    if obligatory_payment == 0:
        raise InvalidTransaction('Obligatory payment amount should be a positive integer.')

    return committee_pub_keys, obligatory_payment, committee_size


class ObligatoryPaymentHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {
            ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT: {
                PB_CLASS: ObligatoryPaymentPayload,
                PROCESSOR: self._pay_obligatory_payment,
                VALIDATOR: ObligatoryPaymentPayloadForm,
            },
        }

    def _pay_obligatory_payment(self, context, node_account_public_key, obligatory_payment_payload):
        node_account_address = NodeAccountHandler().make_address_from_data(node_account_public_key)
        node_account = get_data(context, NodeAccount, node_account_address)
        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        committee_addresses, obligatory_payment, committee_size = get_obligatory_payment_parameters(context)

        address_to_node_account_dict = {
            node_account_address: node_account,
        }
        committee_addresses.remove(node_account_address)  # committee to charge obligatory payment
        
        for address in committee_addresses:
            committee_node_account = get_data(context, NodeAccount, address)
            if committee_node_account is None:
                raise InvalidTransaction('Invalid context or address.')
            withdraw_obligatory_payment(committee_node_account, obligatory_payment)
            address_to_node_account_dict[address] = committee_node_account

        node_account.reputation.unfrozen += (committee_size - 1) * obligatory_payment

        return address_to_node_account_dict
