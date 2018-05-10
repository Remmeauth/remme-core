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
import inspect

import datetime

from remme.atomic_swap_tp.client import AtomicSwapClient, get_swap_init_payload, get_swap_close_payload
from remme.atomic_swap_tp.handler import AtomicSwapHandler
from remme.protos.atomic_swap_pb2 import AtomicSwapMethod, AtomicSwapInfo
from remme.protos.token_pb2 import TokenMethod, GenesisStatus, Account
from remme.settings import SETTINGS_SWAP_COMMISSION
from remme.settings_tp.handler import _make_settings_key
from remme.shared.logging import test
from remme.shared.utils import generate_random_key, hash256
from remme.tests.test_helper import HelperTestCase
from remme.token_tp.client import TokenClient
from remme.token_tp.handler import ZERO_ADDRESS, TokenHandler

LOGGER = logging.getLogger(__name__)


class AtomicSwapTestCase(HelperTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(AtomicSwapHandler)

    @test
    def test_swap_to_local_success(self):
        # 1. Bob init
        # 2. Bob close

        # to be transferred
        AMOUNT = 10000
        COMMISSION = 100
        zero_address = self.handler.make_address(ZERO_ADDRESS)
        swap_id = generate_random_key()
        secret_key = generate_random_key()
        secret_lock = hash256(secret_key)
        now = datetime.datetime.now()
        init_data = {
            "receiver_address": self.account_address2,
            "sender_address_non_local": "any address",
            "amount": AMOUNT,
            "swap_id": swap_id,
            "secret_lock_optional_bob": secret_lock,
            "email_address_encrypted_optional_alice": None,
            "timestamp": now.timestamp(),
        }

        self.send_transaction(AtomicSwapMethod.INIT, get_swap_init_payload(init_data),
                              [swap_id, self.account_address1])

        TOTAL_TRANSFERED = AMOUNT+COMMISSION

        self.expect_get({swap_id: None})
        self.expect_get({_make_settings_key(SETTINGS_SWAP_COMMISSION): COMMISSION})
        self.expect_get({self.account_address1: TokenClient.get_account_model(TOTAL_TRANSFERED)})

        self.transfer(self.account_address1, TOTAL_TRANSFERED, zero_address, 0, TOTAL_TRANSFERED)

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = swap_id
        swap_info.is_closed = False
        swap_info.is_approved = True
        swap_info.amount = AMOUNT
        swap_info.created_at = now
        swap_info.email_address_encrypted_optional_alice = None
        swap_info.sender_address = self.account_address1
        swap_info.sender_addressNonLocal = 'some'
        swap_info.receiver_address = self.account_address2

        self.expect_set({
            swap_id: swap_info,
            zero_address: TokenClient.get_account_model(TOTAL_TRANSFERED),
            self.account_address1: TokenClient.get_account_model(0)
        })

        # close swap

        data = {
            "swap_id": swap_id,
            "secret_key": secret_key
        }

        self.send_transaction(AtomicSwapMethod.CLOSE, get_swap_close_payload(data),
                              [swap_id, self.account_address1])

        self.expect_get({swap_id: swap_info})
        self.transfer(zero_address, AMOUNT, self.account_address2, 0, AMOUNT)

        swap_info.is_closed = True

        self.expect_set({
            swap_id: swap_info,
            zero_address: TokenClient.get_account_model(COMMISSION),
            self.account_address2: TokenClient.get_account_model(AMOUNT)
        })

        self.expect_ok()
