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

import argparse
from remme.protos.token_pb2 import GenesisPayload
from remme.token.token_client import TokenClient
from remme.token.token_handler import TokenHandler, TransactionPayload

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/root/genesis/batch/token-proposal.batch'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    args = parser.parse_args()

    token_client = TokenClient()
    token_handler = TokenHandler()

    zero_address = token_handler.make_address('0' * 64)
    target_address = token_handler.make_address_from_data(token_client.get_signer().get_public_key().as_hex())
    
    print('Issuing tokens to address {}'.format(target_address))

    addresses_input_output = [zero_address, target_address]

    payload = TransactionPayload()
    payload.method = TokenPayload.GENESIS
    payload.data = token_client.get_genesis_payload(args.token_supply).SerializeToString()

    batch_list = TokenClient().make_batch_list(payload.SerializeToString(), addresses_input_output)

    batch_file = open(OUTPUT_BATCH, 'wb')
    batch_file.write(batch_list.SerializeToString())
    batch_file.close()
