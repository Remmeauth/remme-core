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
import logging
import concurrent.futures

from remme.shared.utils import hash512
from remme.protos.account_pb2 import AccountMethod, GenesisPayload, TransferPayload, PubKeyAccount
from remme.clients.basic import BasicClient
from remme.tp.account import AccountHandler
from remme.shared.exceptions import KeyNotFound

from remme.protos.account_pb2 import Account


LOGGER = logging.getLogger(__name__)


class AccountClient(BasicClient):
    def __init__(self):
        super().__init__(AccountHandler)

    def _send_transaction(self, method, data_pb, extra_addresses_input_output):
        addresses_input_output = [self.get_user_address()]
        if extra_addresses_input_output:
            addresses_input_output += extra_addresses_input_output
        return super()._send_transaction(method, data_pb, addresses_input_output)

    @classmethod
    def get_transfer_payload(self, address_to, value):
        transfer = TransferPayload()
        transfer.address_to = address_to
        transfer.value = value

        return transfer

    @classmethod
    def get_genesis_payload(self, total_supply):
        genesis = GenesisPayload()
        genesis.total_supply = int(total_supply)

        return genesis

    @classmethod
    def get_account_model(self, balance):
        account = Account()
        account.balance = int(balance)

        return account

    def transfer(self, address_to, value):
        extra_addresses_input_output = [address_to]
        transfer = self.get_transfer_payload(address_to, value)

        return self._send_transaction(AccountMethod.TRANSFER, transfer, extra_addresses_input_output)

    def get_account(self, address):
        account = Account()
        account.ParseFromString(self.get_value(address))
        return account

    def get_pubkey_account(self, address):
        pubkey_acc = PubKeyAccount()
        pubkey_acc.ParseFromString(self.get_value(address))
        return pubkey_acc

    def get_pub_keys(self, address):
        future_to_address = {}
        pub_keys = []
        try:
            account = self.get_account(address)
        except KeyNotFound:
            return []

        if not account.pub_key_serial_number:
            return pub_keys

        # FIXME: Optimize to one request
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for pk_nonce in range(account.pub_key_serial_number):
                pubkey_acc_address = self.make_address_from_data(f'{address}{pk_nonce}', 'account_pub_key_mapping')
                future_to_address[executor.submit(self.get_pubkey_account, pubkey_acc_address)] = pubkey_acc_address
                LOGGER.debug(f'Submit future for "get_pubkey_account" for pubkey_acc address "{pubkey_acc_address}", '
                             f'where pubkey user address "{address}" and pubkey nonce "{pk_nonce}"')

            for future in concurrent.futures.as_completed(future_to_address):
                try:
                    address = future_to_address[future]
                    pubkey_acc = future.result()
                except KeyNotFound:
                    LOGGER.debug(f'Address "{address}" not found')
                    continue
                except Exception as e:
                    LOGGER.exception(f'Got future error for address "{address}": {e}')
                else:
                    pub_keys.append(pubkey_acc.address)
        return pub_keys

    def get_balance(self, address):
        try:
            account = self.get_account(address)
            return account.balance
        except KeyNotFound:
            return 0
