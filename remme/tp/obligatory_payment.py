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
from sawtooth_validator.journal.batch_injector import BatchInjector
from sawtooth_validator.protobuf.batch_pb2 import (
    Batch,
    BatchHeader,
)

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

        #TODO: implement OP logic.

        if node_account is None:
            node_account = NodeAccount()

        return {
            node_account_address: node_account,
        }


class ObligatoryPaymentInjector(BatchInjector):
    """Inject ObligatoryPayment transaction at the beginning of blocks."""

    def __init__(self, state_view_factory, signer):
        self._state_view_factory = state_view_factory
        self._signer = signer

    def create_batch(self):
        payload = ObligatoryPaymentPayload().SerializeToString()
        public_key = self._signer.get_public_key().as_hex()

        block_signer_address = ObligatoryPaymentHandler().make_address_from_data(data=public_key)

        INPUTS = OUTPUTS = [
            block_signer_address
        ]
        #TODO: also for inputs and outputs need addresses of other masternodes in committee.

        header = TransactionHeader(
            signer_public_key=public_key,
            family_name=FAMILY_NAME,
            family_version=FAMILY_VERSIONS[0],
            inputs=INPUTS,
            outputs=OUTPUTS,
            dependencies=[],
            payload_sha512=hash512(payload).hexdigest(),
            batcher_public_key=public_key,
        ).SerializeToString()

        transaction_signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=transaction_signature,
        )

        header = BatchHeader(
            signer_public_key=public_key,
            transaction_ids=[transaction_signature],
        ).SerializeToString()

        batch_signature = self._signer.sign(header)

        return Batch(
            header=header,
            transactions=[transaction],
            header_signature=batch_signature,
        )

    def block_start(self, previous_block):
        """Returns an ordered list of batches to inject at the beginning of the
        block. Can also return None if no batches should be injected.
        Args:
            previous_block (Block): The previous block.
        Returns:
            A list of batches to inject.
        """

        return [self.create_batch()]

    def before_batch(self, previous_block, batch):
        pass

    def after_batch(self, previous_block, batch):
        pass

    def block_end(self, previous_block, batches):
        pass
