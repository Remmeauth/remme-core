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
from remme.protos.token_pb2 import TokenPayload, Transfer
from remme.protos import token_pb2
from remme.shared.basic_client import BasicClient
from remme.token.token_handler import TokenHandler
from protobuf_to_dict import protobuf_to_dict

from remme.protos.token_pb2 import Account


class TokenClient(BasicClient):
    def __init__(self):
        super().__init__(TokenHandler)

    def _send_transaction(self, method, data_pb, extra_addresses_input_output):
        payload = TokenPayload()
        payload.method = method
        addresses_input_output = [self.make_address_from_data(self._signer.get_public_key().as_hex())]
        if extra_addresses_input_output:
            addresses_input_output += extra_addresses_input_output
        return super()._send_transaction(data_pb, addresses_input_output)

    def transfer(self, address_to, value):
        extra_addresses_input_output = [address_to]

        transfer = Transfer()
        transfer.address_to = address_to
        transfer.value = value
        payload = TokenPayload()
        payload.method = TokenPayload.TRANSFER
        payload.data = transfer.SerializeToString()
        return self._send_transaction(TokenPayload.TRANSFER, transfer, extra_addresses_input_output)

    def get_account(self, address):
        account = Account()
        account.ParseFromString(self.get_value(address))
        return account
