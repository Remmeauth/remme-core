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

sys.path.insert(0, os.getenv('PACKAGE_LOCATION', '/processor'))

import argparse
from processor.protos.token_pb2 import Account

# TODO make address key with the TokenHandler prefix
# TODO fix readability issue from .pub file
# TODO remove b'' during formatting serialized proto to string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    parser.add_argument('key_file')
    args = parser.parse_args()

    account = Account()
    account.balance = int(args.token_supply)

    assert(os.path.exists(args.key_file))
    with open(args.key_file, 'w+') as output_file:
        with open(args.key_address, 'r') as pub_key:
            key = args.key_address
            print('sawset proposal create {}={}'.format(key, account.SerializeToString()))
