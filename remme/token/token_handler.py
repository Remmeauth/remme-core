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

from google.protobuf.text_format import ParseError
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.token_pb2 import Account, Transfer, TokenPayload, Genesis, GenesisStatus
from remme.shared.basic_handler import *

ZERO_ADDRESS = '0' * 64

FAMILY_NAME = 'token'
FAMILY_VERSIONS = ['0.1']


# TODO: ensure receiver_account.balance += params.amount is within uint64
class TokenHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)
        self.zero_address = self.make_address(ZERO_ADDRESS)

    def apply(self, transaction, context):
        super().process_apply(context, TokenPayload, transaction)

    def process_state(self, context, signer_pubkey, payload):
        process_transaction = None
        data_payload = None
        if payload.method == TokenPayload.TRANSFER:
            data_payload = Transfer()
            process_transaction = self.transfer
        elif payload.method == TokenPayload.GENESIS:
            data_payload = Genesis()
            process_transaction = self.genesis

        if not process_transaction or not data_payload:
            raise InvalidTransaction("Not a valid transaction method {}".format(payload.method))

        try:
            data_payload.ParseFromString(payload.data)
        except ParseError:
            raise InvalidTransaction("Invalid data serialization for method {}".format(payload.method))

        address = self.make_address_from_data(signer_pubkey)
        account = self.get_data(context, Account, address)

        return process_transaction(context, address, account, data_payload)

    def genesis(self, context, signer, signer_account, data_payload):
        genesis_status = self.get_data(context, GenesisStatus, self.zero_address)
        if genesis_status.status:
            raise InvalidTransaction('Genesis is already initialized.')
        genesis_status.status = True
        account = Account()
        account.balance = data_payload.total_supply
        return {
            signer: account,
            self.zero_address: genesis_status
        }

    def transfer(self, context, signer_address, signer_account, params):
        receiver_account = self.get_data(context, Account, params.address_to)

        if signer_account.balance < params.value:
            raise InvalidTransaction("Not enough transferable balance. Signer's current balance: {}"
                                     .format(signer_account.balance))

        receiver_account.balance += params.value
        signer_account.balance -= params.value

        return {
            signer_address: signer_account,
            params.address_to: receiver_account
        }
