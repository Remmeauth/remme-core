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

# pylint: disable=invalid-name

import argparse
from remme.protos.account_pb2 import AccountMethod
from remme.protos.transaction_pb2 import TransactionPayload

from remme.clients.account import AccountClient
from remme.tp.account import AccountHandler
from remme.settings import GENESIS_ADDRESS
from remme.settings.default import load_toml_with_defaults

OUTPUT_BATCH = '/genesis/batch/token-proposal.batch'

if __name__ == '__main__':
    parameters = load_toml_with_defaults('/config/remme-genesis-config.toml')['remme']['genesis']

    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('--token-supply', default=parameters['token_supply'])
    args = parser.parse_args()

    account_client = AccountClient()

    if parameters['economy_enabled']:
        zero_address = AccountHandler().make_address('0' * 64)
        target_address = AccountHandler().make_address_from_data(account_client.get_signer().get_public_key().as_hex())

        print('Issuing {} tokens to address {}'.format(args.token_supply, target_address))

        addresses_input = [GENESIS_ADDRESS]
        addresses_output = [GENESIS_ADDRESS, target_address]

        payload = TransactionPayload()
        payload.method = AccountMethod.GENESIS
        payload.data = account_client.get_genesis_payload(args.token_supply).SerializeToString()

        batch_list = AccountClient().make_batch_list(payload, addresses_input, addresses_output)

        batch_file = open(OUTPUT_BATCH, 'wb')
        batch_file.write(batch_list.SerializeToString())
        batch_file.close()
