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
import sys
import os
import argparse
from processor.protos.token_pb2 import Account
from processor.settings import PUB_KEY_FILE, PRIV_KEY_FILE
from processor.token.token_handler import TokenHandler

# HOW TO RUN
# 1. In shell generate needed key `sawtooth keygen key`
# 2. python3 genesis/generate_token_genesis.py <token supply>

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/genesis/token-proposal.batch'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    args = parser.parse_args()

    account = Account()
    account.balance = int(args.token_supply)

    assert(os.path.exists(PUB_KEY_FILE))
    with open(OUTPUT_SH, 'w+') as output_file:
        with open(PUB_KEY_FILE, 'r') as pub_key:
            key = TokenHandler().make_address(pub_key.read().replace('\n', ''))
            print(key)
            value = str(account.SerializeToString())[2:-1]
            output_file.write('sawset proposal create -o {} -k {} {}={} '.format(OUTPUT_BATCH, PRIV_KEY_FILE, key, value))