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

from remme.protos.token_pb2 import Account, Transfer, TokenPayload, Genesis, GenesisStatus
from remme.shared.basic_handler import *

FAMILY_NAME = 'token'
FAMILY_VERSIONS = ['0.1']


# TODO: ensure receiver_account.balance += params.amount is within uint64
class TokenHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)
        self.zero_address = self._prefix + '0' * 64

    def apply(self, transaction, context):
        super().process_apply(transaction, context, Account)

        # returns updated state
    def process_state(self, signer_pubkey, signer, payload):
        signer_account = self._get_data(Account, signer)
        token_payload = TokenPayload()
        try:
            token_payload.ParseFromString(payload)
        except:
            raise InvalidTransaction("Invalid payload serialization!")

        process_transaction = None
        data_payload = None
        if token_payload.method == TokenPayload.TRANSFER:
            data_payload = Transfer()
            process_transaction = self.transfer
        elif token_payload.method == TokenPayload.GENESIS:
            data_payload = Genesis()
            process_transaction = self.genesis

        if not process_transaction or not data_payload:
            raise InvalidTransaction("Not a valid transaction method {}".format(token_payload.method))

        try:
            data_payload.ParseFromString(token_payload.data)
        except:
            raise InvalidTransaction("Invalid data serialization for method {}".format(token_payload.method))

        return process_transaction(signer, signer_account, data_payload)

    def genesis(self, signer, signer_account, data_payload):
        zero_address = self._get_state(self.zero_address)
        genesis_status = GenesisStatus()
        if zero_address:
            genesis_status.ParseFromString(zero_address)

        if genesis_status.status:
            raise InvalidTransaction('Genesis is already initialized.')

        genesis_status.status = True

        account = Account()
        account.balance = data_payload.total_supply
        return {
            signer: account,
            self.zero_address: genesis_status
        }

    def transfer(self, signer_address, signer_account, params):
        if params.address_to == signer_address:
            raise InvalidTransaction("Transaction cannot be sent to the same same address as of the sender!")
        if self.zero_address in [params.address_to, signer_address]:
            raise InvalidTransaction("Zero address cannot send, nor receive transfers!")
        if not self.is_address(params.address_to):
            raise InvalidTransaction("address_to parameter passed: {} is not an address.".format(params.address_to))
        receiver_account = self._get_data(Account, params.address_to)

        if signer_account.balance < params.value:
            raise InvalidTransaction("Not enough transferable balance. Signer's current balance: {}".format(signer_account.balance))


        receiver_account.balance += params.value
        signer_account.balance -= params.value

        return { signer_address: signer_account,
                 params.address_to: receiver_account}
