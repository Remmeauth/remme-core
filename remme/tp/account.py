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
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.account_pb2 import (
    Account, GenesisStatus, AccountMethod, GenesisPayload,
    TransferPayload
)
from remme.settings.helper import _get_setting_value
from remme.settings import GENESIS_ADDRESS, ZERO_ADDRESS, SETTINGS_KEY_GENESIS_OWNERS
from remme.tp.basic import PB_CLASS, PROCESSOR, BasicHandler, get_data, get_multiple_data
from remme.shared.constants import Events, EMIT_EVENT


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'account'
FAMILY_VERSIONS = ['0.1']


def get_account_by_address(context, address):
    account = get_data(context, Account, address)
    if account is None:
        return Account()
    return account


# TODO: ensure receiver_account.balance += transfer_payload.amount is within uint64
class AccountHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    @classmethod
    def create_transfer(cls, context, address_from, address_to, amount):
        transfer_payload = TransferPayload(address_to=address_to, value=amount)
        return cls() \
            ._transfer_from_address(context, address_from, transfer_payload)

    def get_state_processor(self):
        return {
            AccountMethod.TRANSFER: {
                PB_CLASS: TransferPayload,
                PROCESSOR: self._transfer,
                EMIT_EVENT: Events.ACCOUNT_TRANSFER.value
            },
            AccountMethod.GENESIS: {
                PB_CLASS: GenesisPayload,
                PROCESSOR: self._genesis
            }
        }

    def _genesis(self, context, pub_key, genesis_payload):
        signer_key = self.make_address_from_data(pub_key)
        genesis_status = get_data(context, GenesisStatus, GENESIS_ADDRESS)
        if not genesis_status:
            genesis_status = GenesisStatus()
        elif genesis_status.status:
            raise InvalidTransaction('Genesis is already initialized.')
        genesis_status.status = True
        account = Account()
        account.balance = genesis_payload.total_supply
        LOGGER.info('Generated genesis transaction. Issued {} tokens to address {}'
                    .format(genesis_payload.total_supply, signer_key))
        return {
            signer_key: account,
            GENESIS_ADDRESS: genesis_status
        }

    def _transfer(self, context, pub_key, transfer_payload):
        address = self.make_address_from_data(pub_key)
        LOGGER.info('pub_key: {} address: {}'.format(pub_key, address))
        if address == ZERO_ADDRESS:
            raise InvalidTransaction("Public transfers are not allowed from ZERO_ADDRESS"
                                     " (which is used for internal transactions")

        if not transfer_payload.address_to.startswith(self._prefix) \
                and transfer_payload.address_to not in [ZERO_ADDRESS]:
            raise InvalidTransaction("Receiver address has to be of "
                                     "an account type")
        return self._transfer_from_address(context, address, transfer_payload)

    def _check_signer_address(self, context, signer_address):
        genesis_members_str = _get_setting_value(context,
                                                 SETTINGS_KEY_GENESIS_OWNERS)
        if not genesis_members_str:
            raise InvalidTransaction('REMchain is not configured '
                                     'to process genesis transfers.')

        genesis_members_list = list(map(lambda el: self.make_address_from_data(el),
                                        genesis_members_str.split(',')))

        LOGGER.debug(f'GENESIS MEMBERS ADDRESSES: {genesis_members_list}')

        if signer_address not in genesis_members_list:
            raise InvalidTransaction(
                f'Signer address "{signer_address}" '
                'not in genesis members list')

    def _transfer_from_address(self, context, address, transfer_payload):
        signer_key = address

        if not transfer_payload.value:
            raise InvalidTransaction("Could not transfer with zero amount")

        if not transfer_payload.address_to.startswith(self._prefix) \
                and transfer_payload.address_to not in [ZERO_ADDRESS]:
            raise InvalidTransaction("Receiver address has to be of an account type")

        if signer_key == transfer_payload.address_to:
            raise InvalidTransaction("Account cannot send tokens to itself.")

        signer_account, receiver_account = get_multiple_data(context, [
            (signer_key, Account),
            (transfer_payload.address_to, Account)
        ])

        if not receiver_account:
            receiver_account = Account()
        if not signer_account:
            signer_account = Account()

        if signer_account.balance < transfer_payload.value:
            raise InvalidTransaction(
                "Not enough transferable balance. Sender's current balance: "
                f"{signer_account.balance}")

        receiver_account.balance += transfer_payload.value
        signer_account.balance -= transfer_payload.value

        LOGGER.info(f'Transferred {transfer_payload.value} tokens from '
                    f'{signer_key} to {transfer_payload.address_to}')

        return {
            signer_key: signer_account,
            transfer_payload.address_to: receiver_account
        }
