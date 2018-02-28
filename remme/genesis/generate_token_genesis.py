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
import hashlib
import time
from remme.protos.token_pb2 import Genesis, TokenPayload
from remme.token.token_client import TokenClient
from remme.token.token_handler import TokenHandler
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from remme.shared.exceptions import ClientException
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing import create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from remme.settings import PUB_KEY_FILE, PRIV_KEY_FILE

# HOW TO RUN
# 1. In shell generate needed key `sawtooth keygen key`
# 2. python3 genesis/generate_token_genesis.py <token supply>
from remme.shared.basic_client import _sha512

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/root/genesis/token-proposal.batch'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    args = parser.parse_args()

    token_client = TokenClient()
    genesis = Genesis()
    genesis.total_supply = int(args.token_supply)

    payload = TokenPayload()
    payload.method = TokenPayload.GENESIS
    payload.data = genesis.SerializeToString()

    handler = TokenHandler()

    zero_address = handler.namespaces[-1] + '0' * 64
    target_address = handler.make_address_from_data(token_client.get_signer().get_public_key().as_hex())
    
    print('Issuing tokens to address {}'.format(target_address))

    addresses_input_output = [zero_address, target_address]

    batch_list = TokenClient()._make_batch_list(payload, addresses_input_output)

    batch_file = open(OUTPUT_BATCH, 'wb')
    batch_file.write(batch_list.SerializeToString())
    batch_file.close()
