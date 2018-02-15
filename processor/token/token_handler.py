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

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from processor.protos.token_pb2 import Account, Transfer
from processor.remme_transaction_processor.basic_handler import *

FAMILY_NAME = 'token'
FAMILY_VERSIONS = ['0.1']

# TODO: ensure receiver_account.balance += params.amount is within uint64

METHOD_TRANSFER = 'transfer'

class TokenHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def apply(self, transaction, context):
        super().process_apply(transaction, context, Account)

        # returns updated state
    def process_state(self, signer, method, data, signer_account):
        process_transaction = None
        data_payload = None
        if method == METHOD_TRANSFER:
            data_payload = Transfer()
            process_transaction = self.transfer

        if not process_transaction or not data_payload:
            raise InvalidTransaction("Not a valid transaction method {}".format(method))

        try:
            data_payload.ParseFromString(data)
        except:
            raise InvalidTransaction("Invalid data serialization for method {}".format(method))

        return process_transaction(signer, signer_account, data_payload)

    def transfer(self, signer, signer_account, params):
        if not self.is_address(params.address_to):
            raise InvalidTransaction("address_to parameter passed: {} is not an address.".format(params.address_to))
        receiver_account = self._get_data(Account, params.address_to)

        if signer_account.balance < params.amount:
            raise InvalidTransaction("Not enough transferable balance. Signer's current balance: {}".format(signer_account.balance))


        receiver_account.balance += params.amount
        signer_account.balance -= params.amount

        return { signer: signer_account,
                 params.address_to: receiver_account}
