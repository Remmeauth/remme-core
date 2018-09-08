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
from remme.settings import GENESIS_ADDRESS, ZERO_ADDRESS
from remme.tp.basic import *

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

    def get_state_processor(self):
        return {
            AccountMethod.TRANSFER: {
                'pb_class': TransferPayload,
                'processor': self._transfer
            },
            AccountMethod.GENESIS: {
                'pb_class': GenesisPayload,
                'processor': self._genesis
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
