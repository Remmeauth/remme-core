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
from processor.protos.token_pb2 import TokenPayload, Transfer
from processor.protos import token_pb2
from processor.shared.basic_client import BasicClient
from processor.token.token_handler import TokenHandler
from protobuf_to_dict import protobuf_to_dict

class TokenClient(BasicClient):
    def __init__(self):
        super().__init__(TokenHandler)

    def _send_transaction(self, method, data, extra_addresses_input_output):
        addresses_input_output = [self.make_address(self._signer.get_public_key().as_hex())]
        if extra_addresses_input_output:
            addresses_input_output += extra_addresses_input_output
        return super()._send_transaction(method, data, addresses_input_output)

    def transfer(self, address_to, value):
        extra_addresses_input_output = [address_to]
        transfer = Transfer()
        transfer.address_to = address_to
        transfer.value = value
        return self._send_transaction(TokenPayload.TRANSFER, protobuf_to_dict(transfer), extra_addresses_input_output)

    def get_account(self, address):
        return self.get_value(address)


