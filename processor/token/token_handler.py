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
from processor.protos.token_pb2 import Account, Transfer
from .helpers import *

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'token'
FAMILY_VERSIONS = ['0.1']


# TODO: ensure receiver_account.balance += params.amount is within uint64
class TokenHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)
        LOGGER.info('Started REM token operations transactions handler.')

    def apply(self, transaction, context):
        super().process_apply(transaction, context, Account)

    # returns updated state
    def process_state(self, signer, data, signer_account):
        data_payload = None

        try:
            data_payload.ParseFromString(data)
        except:
            raise InvalidTransaction("Invalid data serialization for a token transaction")

        return transfer(signer, signer_account, data_payload)

    def transfer(self, signer, signer_account, params):
        receiver_account = self._get_data(Account, params.address_to)

        if signer_account.balance < params.amount:
            raise InvalidTransaction("Not enough transferable balance. Signer's current balance: {}"
                                     .format(signer_account.balance))

        receiver_account.balance += params.amount
        signer_account.balance -= params.amount

        return {signer: signer_account,
                params.address_to: receiver_account}
