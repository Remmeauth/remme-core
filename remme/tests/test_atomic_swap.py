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
from remme.protos.settings_pb2 import Setting
from remme.protos.token_pb2 import TokenMethod, GenesisStatus, Account
from remme.settings import SETTINGS_SWAP_COMMISSION
from remme.settings_tp.handler import _make_settings_key, get_setting_from_key_value
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

        # to be transferred
        cls.AMOUNT = 10000
        cls.COMMISSION = 100

        cls.swap_id = generate_random_key()
        cls.swap_address = cls.handler.make_address(cls.swap_id)
        cls.secret_key = generate_random_key()
        cls.secret_lock = hash256(cls.secret_key)
        cls.now = datetime.datetime.now()
        cls.created_at = int(cls.now.timestamp())
        cls.email_address = ""
        cls.sender_address_non_local = ""
        cls.init_data = {
            "receiver_address": cls.account_address2,
            "sender_address_non_local": cls.sender_address_non_local,
            "amount": cls.AMOUNT,
            "swap_id": cls.swap_id,
            "secret_lock_optional_bob": cls.secret_lock,
            "email_address_encrypted_optional_alice": cls.email_address,
            "created_at": cls.created_at,
        }

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = cls.swap_id
        swap_info.is_closed = False
        swap_info.is_approved = True
        swap_info.is_initiator = False
        swap_info.amount = cls.AMOUNT
        swap_info.created_at = cls.created_at
        swap_info.email_address_encrypted_optional = cls.email_address
        swap_info.sender_address = cls.account_address1
        swap_info.sender_address_non_local = cls.sender_address_non_local
        swap_info.receiver_address = cls.account_address2
        swap_info.secret_lock = cls.secret_lock
        cls.swap_info = swap_info

    @test
    def test_swap_init_success(self):
        # Bob init

        self.send_transaction(AtomicSwapMethod.INIT, get_swap_init_payload(self.init_data),
                              [self.swap_id, self.account_address1])

        TOTAL_TRANSFERED = self.AMOUNT+self.COMMISSION

        self.expect_get({self.swap_address: None})

        self.expect_get({
            _make_settings_key(SETTINGS_SWAP_COMMISSION):
                get_setting_from_key_value(SETTINGS_SWAP_COMMISSION, self.COMMISSION)
        })
        self.expect_get({self.account_address1: TokenClient.get_account_model(TOTAL_TRANSFERED)})

        updated_state = self.transfer(self.account_address1, TOTAL_TRANSFERED, ZERO_ADDRESS, 0, TOTAL_TRANSFERED)

        self.expect_set({
            **{self.swap_address: self.swap_info},
            **updated_state
        })

        self.expect_ok()

    @test
    def test_swap_close_success(self):
        close_data = {
            "swap_id": self.swap_id,
            "secret_key": self.secret_key
        }

        self.send_transaction(AtomicSwapMethod.CLOSE, get_swap_close_payload(close_data),
                              [self.swap_id, self.account_address1])

        self.expect_get({self.swap_address: self.swap_info})
        updated_state = self.transfer(ZERO_ADDRESS, self.AMOUNT, self.account_address2, 0, self.AMOUNT)

        swap_info = self.swap_info
        swap_info.is_closed = True

        self.expect_set({
            **{self.swap_address: swap_info},
            **updated_state
        })

        self.expect_ok()
