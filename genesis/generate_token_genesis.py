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

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/genesis/token-proposal.batch'
SIGNING_KEY = '/root/.sawtooth/keys/my_key.priv'
KEY_FILE = 'keys/my_key.pub'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    parser.add_argument('key_file')
    args = parser.parse_args()

    account = Account()
    account.balance = int(args.token_supply)

    assert(os.path.exists(KEY_FILE))
    with open(OUTPUT_SH, 'w+') as output_file:
        with open(KEY_FILE, 'r') as pub_key:
            key = pub_key.read()
            # value = 'value'
            value = str(account.SerializeToString())[2:-1]
            output_file.write('sawset proposal create -o {} -k {} {}={} '.format(OUTPUT_BATCH, SIGNING_KEY, key[:-1], value))