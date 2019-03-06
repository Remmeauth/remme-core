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
    NodeAccount
)
from remme.settings import (
    CONSENSUS_ALLOWED_VALIDATORS,
    SETTINGS_OBLIGATORY_PAYMENT,
    SETTINGS_COMMITTEE_SIZE,
)

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
    committee_pub_keys = _get_setting_value(context, CONSENSUS_ALLOWED_VALIDATORS)
    if committee_pub_keys is None or type(committee_pub_keys) != str:
        raise InvalidTransaction('remme.consensus.allowed_validators is malformed. Should be list of public keys.')
    committee_pub_keys = committee_pub_keys.split(';')

    obligatory_payment = _get_setting_value(context, SETTINGS_OBLIGATORY_PAYMENT)
    if obligatory_payment is None and not obligatory_payment.isdigit():
        raise InvalidTransaction('remme.settings.obligatory_payment is malformed. Should be positive integer.')
    obligatory_payment = int(obligatory_payment)

    committee_size = _get_setting_value(context, SETTINGS_COMMITTEE_SIZE)
    if committee_size is None and not committee_size.isdigit():
        raise InvalidTransaction('remme.settings.committe_size is malformed. Should be positive integer.')
    committee_size = int(committee_size)

    if len(committee_pub_keys) != committee_size:
        raise InvalidTransaction('Malformed committee.')

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
        node_account_address = self.make_address_from_data(node_account_public_key)
        node_account = get_data(context, NodeAccount, node_account_address)

        if node_account is None:
            raise InvalidTransaction('Invalid context or address.')

        committee_pub_keys, obligatory_payment, committee_size = get_obligatory_payment_parameters(context)

        address_to_node_account_dict = {
            node_account_address: node_account,
        }
        committee_pub_keys.remove(node_account_public_key)  # committee to charge obligatory payment
        for pub_key in committee_pub_keys:

            address = self.make_address_from_data(pub_key)
            committee_node_account = get_data(context, NodeAccount, address)

            if committee_node_account is None:
                raise InvalidTransaction('Invalid context or address.')

            withdraw_obligatory_payment(committee_node_account, obligatory_payment)

            address_to_node_account_dict[address] = committee_node_account

        node_account.reputation.unfrozen += (committee_size-1)*obligatory_payment

        return address_to_node_account_dict
