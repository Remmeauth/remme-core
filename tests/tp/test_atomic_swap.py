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

import datetime

from remme.clients.atomic_swap import AtomicSwapClient, get_swap_init_payload, get_swap_close_payload, \
    get_swap_approve_payload, get_swap_expire_payload, get_swap_set_secret_lock_payload
from remme.tp.atomic_swap import AtomicSwapHandler
from remme.protos.atomic_swap_pb2 import AtomicSwapInfo
from remme.settings import SETTINGS_SWAP_COMMISSION
from remme.settings.helper import _make_settings_key, get_setting_from_key_value
from remme.shared.logging import test
from remme.shared.utils import generate_random_key, hash256, web3_hash
from tests.test_helper import HelperTestCase
from remme.clients.account import AccountClient
from remme.tp.account import ZERO_ADDRESS

LOGGER = logging.getLogger(__name__)


class AtomicSwapTestCase(HelperTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(AtomicSwapHandler, AtomicSwapClient)

    def get_context(self):
        context = super().get_context()
        context.AMOUNT = 10000
        context.COMMISSION = 100

        context.swap_id = generate_random_key()
        context.swap_address = AtomicSwapHandler.make_address_from_data(context.swap_id)
        context.secret_key = "039eaa877ff63694f8f09c8034403f8b5165a7418812a642396d5d539f90b170"
        context.secret_lock = "b605112c2d7489034bbd7beab083fb65ba02af787786bb5e3d99bb26709f4f68"
        context.now = datetime.datetime.now()
        context.created_at = int(context.now.timestamp())
        context.email_address = ""
        context.sender_address_non_local = ""

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = context.swap_id
        swap_info.is_closed = False
        swap_info.is_expired = False
        swap_info.is_approved = True
        swap_info.is_initiator = False
        swap_info.amount = context.AMOUNT
        swap_info.created_at = context.created_at
        swap_info.email_address_encrypted_optional = context.email_address
        swap_info.sender_address = self.account_address1
        swap_info.sender_address_non_local = context.sender_address_non_local
        swap_info.receiver_address = self.account_address2
        swap_info.secret_lock = context.secret_lock
        context.swap_info = swap_info
        return context

    # TEST: INIT
    @test
    def test_swap_init_success(self):
        # Bob init

        context = self.get_context()
        init_data = {
            "receiver_address": self.account_address2,
            "sender_address_non_local": context.sender_address_non_local,
            "amount": context.AMOUNT,
            "swap_id": context.swap_id,
            "secret_lock_by_solicitor": context.secret_lock,
            "email_address_encrypted_by_initiator": context.email_address,
            "created_at": context.created_at,
        }

        context.client.swap_init(get_swap_init_payload(**init_data))

        self.expect_get({context.swap_address: None})

        self.expect_get({
            _make_settings_key(SETTINGS_SWAP_COMMISSION):
                get_setting_from_key_value(SETTINGS_SWAP_COMMISSION, context.COMMISSION)
        })

        TOTAL_TRANSFERED = context.AMOUNT+context.COMMISSION
        self.expect_get({self.account_address1: AccountClient.get_account_model(TOTAL_TRANSFERED)})

        updated_state = self.transfer(self.account_address1, TOTAL_TRANSFERED, ZERO_ADDRESS, 0, TOTAL_TRANSFERED)

        self.expect_set({
            **{context.swap_address: context.swap_info},
            **updated_state
        })

        self.expect_ok()

    @test
    def test_swap_init_fail_swap_exists(self):
        context = self.get_context()
        init_data = {
            "receiver_address": self.account_address2,
            "sender_address_non_local": context.sender_address_non_local,
            "amount": context.AMOUNT,
            "swap_id": context.swap_id,
            "secret_lock_by_solicitor": context.secret_lock,
            "email_address_encrypted_by_initiator": context.email_address,
            "created_at": context.created_at,
        }

        context.client.swap_init(get_swap_init_payload(**init_data))

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_init_fail_created_long_time_ago(self):
        context = self.get_context()
        init_data = {
            "receiver_address": self.account_address2,
            "sender_address_non_local": context.sender_address_non_local,
            "amount": context.AMOUNT,
            "swap_id": context.swap_id,
            "secret_lock_by_solicitor": context.secret_lock,
            "email_address_encrypted_by_initiator": context.email_address,
            "created_at": int((datetime.datetime.now() - datetime.timedelta(days=2)).timestamp()),
        }

        context.client.swap_init(get_swap_init_payload(**init_data))

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_init_fail_wrong_receiver_address(self):
        context = self.get_context()
        init_data = {
            "receiver_address": context.swap_address,
            "sender_address_non_local": context.sender_address_non_local,
            "amount": context.AMOUNT,
            "swap_id": context.swap_id,
            "secret_lock_by_solicitor": context.secret_lock,
            "email_address_encrypted_by_initiator": context.email_address,
            "created_at": int((datetime.datetime.utcnow() - datetime.timedelta(days=2)).timestamp()),
        }

        context.client.swap_init(get_swap_init_payload(**init_data))

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    # END TEST

    # TEST: CLOSE

    @test
    def test_swap_close_success(self):
        context = self.get_context()
        close_data = {
            "swap_id": context.swap_id,
            "secret_key": context.secret_key
        }

        context.client.swap_close(get_swap_close_payload(**close_data), context.swap_info.receiver_address)

        self.expect_get({context.swap_address: context.swap_info})
        updated_state = self.transfer(ZERO_ADDRESS, context.AMOUNT, self.account_address2, 0, context.AMOUNT)

        swap_info = context.swap_info
        swap_info.is_closed = True
        swap_info.secret_key = context.secret_key

        self.expect_set({
            **{context.swap_address: swap_info},
            **updated_state
        })

        self.expect_ok()

    @test
    def test_swap_close_fail_no_secret_lock(self):
        context = self.get_context()
        close_data = {
            "swap_id": context.swap_id,
            "secret_key": context.secret_key
        }

        context.client.swap_close(get_swap_close_payload(**close_data), context.swap_info.receiver_address)

        context.swap_info.secret_lock = ""
        self.expect_get({context.swap_address: context.swap_info})
        self.expect_invalid_transaction()

    @test
    def test_swap_close_fail_wrong_secret_key(self):
        context = self.get_context()
        close_data = {
            "swap_id": context.swap_id,
            "secret_key": context.secret_key[:-1] + '1'
        }

        context.client.swap_close(get_swap_close_payload(**close_data), context.swap_info.receiver_address)

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_close_fail_not_approved(self):
        context = self.get_context()
        close_data = {
            "swap_id": context.swap_id,
            "secret_key": context.secret_key
        }

        context.client.swap_close(get_swap_close_payload(**close_data), context.swap_info.receiver_address)

        context.swap_info.is_approved = False
        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    # END TEST

    # TEST: APPROVE

    @test
    def test_swap_approve_success(self):
        context = self.get_context()
        approve_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_approve(get_swap_approve_payload(**approve_data))

        context.swap_info.is_initiator = True

        self.expect_get({context.swap_address: context.swap_info})
        context.swap_info.is_approved = True

        self.expect_set({context.swap_address: context.swap_info})

        self.expect_ok()
    #
    @test
    def test_swap_approve_fail_not_initiator(self):
        context = self.get_context()
        approve_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_approve(get_swap_approve_payload(**approve_data))

        context.swap_info.is_initiator = False

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_approve_fail_no_secret_lock(self):
        context = self.get_context()
        approve_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_approve(get_swap_approve_payload(**approve_data))

        context.swap_info.is_initiator = True
        context.swap_info.secret_lock = ""

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_approve_fail_is_closed(self):
        context = self.get_context()
        approve_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_approve(get_swap_approve_payload(**approve_data))

        context.swap_info.is_closed = True

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    # END TEST

    # TEST: EXPIRE

    @test
    def test_swap_expire_success_initiator(self):
        context = self.get_context()
        expire_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_expire(get_swap_expire_payload(**expire_data))

        context.swap_info.created_at = int((datetime.datetime.utcnow() - datetime.timedelta(days=1, minutes=1)).timestamp())
        context.swap_info.is_initiator = True

        self.expect_get({context.swap_address: context.swap_info})

        updated_state = self.transfer(ZERO_ADDRESS, context.swap_info.amount, self.account_address1, 0, context.swap_info.amount)
        context.swap_info.is_closed = True
        context.swap_info.is_expired = True

        self.expect_set({
            **{context.swap_address: context.swap_info},
            **updated_state
        })

        self.expect_ok()

    @test
    def test_swap_expire_success_non_initiator(self):
        context = self.get_context()
        expire_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_expire(get_swap_expire_payload(**expire_data))

        context.swap_info.created_at = int(
            (datetime.datetime.utcnow() - datetime.timedelta(days=2, minutes=1)).timestamp())
        context.swap_info.is_initiator = False

        self.expect_get({context.swap_address: context.swap_info})

        updated_state = self.transfer(ZERO_ADDRESS, context.swap_info.amount, self.account_address1, 0,
                                      context.swap_info.amount)
        context.swap_info.is_closed = True
        context.swap_info.is_expired = True

        self.expect_set({
            **{context.swap_address: context.swap_info},
            **updated_state
        })

        self.expect_ok()

    @test
    def test_swap_expire_fail_wrong_signer(self):
        context = self.get_context()
        expire_data = {
            "swap_id": context.swap_id,
        }

        context.client.set_signer(self.account_signer2)
        context.client.swap_expire(get_swap_expire_payload(**expire_data))

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_expire_fail_early_non_initiator(self):
        context = self.get_context()
        expire_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_expire(get_swap_expire_payload(**expire_data))

        context.swap_info.created_at = int(
            (datetime.datetime.utcnow() - datetime.timedelta(days=1, minutes=1)).timestamp())
        context.swap_info.is_initiator = False

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    @test
    def test_swap_expire_fail_early_initiator(self):
        context = self.get_context()
        expire_data = {
            "swap_id": context.swap_id,
        }

        context.client.swap_expire(get_swap_expire_payload(**expire_data))

        context.swap_info.created_at = int(
            (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).timestamp())
        context.swap_info.is_initiator = True

        self.expect_get({context.swap_address: context.swap_info})

        self.expect_invalid_transaction()

    # END TEST

    # TEST: SET-LOCK

    @test
    def test_swap_set_lock_success(self):
        context = self.get_context()
        set_secert_lock_data = {
            "swap_id": context.swap_id,
            "secret_lock": context.secret_lock,
        }

        context.client.swap_set_secret_lock(get_swap_set_secret_lock_payload(**set_secert_lock_data))

        context.swap_info.secret_lock = ""

        self.expect_get({context.swap_address: context.swap_info})
        context.swap_info.secret_lock = context.secret_lock

        self.expect_set({context.swap_address: context.swap_info})

        self.expect_ok()

    @test
    def test_swap_set_lock_fail_already_set(self):
        context = self.get_context()
        set_secert_lock_data = {
            "swap_id": context.swap_id,
            "secret_lock": context.secret_lock,
        }

        context.client.swap_set_secret_lock(get_swap_set_secret_lock_payload(**set_secert_lock_data))

        context.swap_info.secret_lock = context.secret_lock

        self.expect_get({context.swap_address: context.swap_info})
        self.expect_invalid_transaction()

    # END TEST
