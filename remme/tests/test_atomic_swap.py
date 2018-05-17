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

from remme.atomic_swap_tp.client import AtomicSwapClient, get_swap_init_payload, get_swap_close_payload, \
    get_swap_approve_payload, get_swap_expire_payload, get_swap_set_secret_lock_payload
from remme.atomic_swap_tp.handler import AtomicSwapHandler
from remme.protos.atomic_swap_pb2 import AtomicSwapMethod, AtomicSwapInfo
from remme.protos.settings_pb2 import Setting
from remme.protos.token_pb2 import TokenMethod, GenesisStatus, Account
from remme.settings import SETTINGS_SWAP_COMMISSION
from remme.settings.helper import _make_settings_key, get_setting_from_key_value
from remme.shared.logging import test
from remme.shared.utils import generate_random_key, hash256, AttrDict
from remme.tests.test_helper import HelperTestCase
from remme.token_tp.client import TokenClient
from remme.token_tp.handler import ZERO_ADDRESS, TokenHandler

LOGGER = logging.getLogger(__name__)


# TO GET THE LATEST TIMESTAMP
# https://www.unixtimestamp.com/
#
# MANUAL TEST REST API
# 1. ETH => REMchain (Bob Actions)
# /init/
# {
#   "amount": 10000,
#   "created_at": 1526293647,
#   "email_address_encrypted_optional_alice": "",
#   "is_initiator": false,
#   "receiver_address": "2265da5c1a648002310b7360b38d82e0b6357e42d49fb1d6b8b33b2fad7a659f2d4e44",
#   "secret_lock_optional_bob": "8bc9d977e4d5ef40f1a61fb60b687eb1924cd90ed4061f31923f36a057f54ce5",
#   "sender_address_non_local": "",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
# expire/
# Expected behaviour: asked to wait 48 hours
# {
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
# close/
# {
#   "secret_key": "747f9238d844e6ae6239df18716bb3dc486e6a9dee7ed6630f8aa6f05946440b",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# 2. REMchain => ETH (Alice Actions)
#
# init/
# {
#   "amount": 10000,
#   "created_at": 1526391085,
#   "email_address_encrypted_optional_alice": "",
#   "is_initiator": false,
#   "receiver_address": "2265da5c1a648002310b7360b38d82e0b6357e42d49fb1d6b8b33b2fad7a659f2d4e44",
#   "sender_address_non_local": "",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# expire/
# Expected behaviour: wait for 24 hours
# {
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# set-secret-lock/
# {
#   "secret_lock": "8bc9d977e4d5ef40f1a61fb60b687eb1924cd90ed4061f31923f36a057f54ce5",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# approve/
# {
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# close/
# {
#   "secret_key": "747f9238d844e6ae6239df18716bb3dc486e6a9dee7ed6630f8aa6f05946440b",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }
#
# {
#   "secret_key": "747f9238d844e6ae6239df18716bb3dc486e6a9dee7ed6630f8aa6f05946440b",
#   "swap_id": "033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce482c"
# }

# secret key: 747f9238d844e6ae6239df18716bb3dc486e6a9dee7ed6630f8aa6f05946440b
# secret_lock: 8bc9d977e4d5ef40f1a61fb60b687eb1924cd90ed4061f31923f36a057f54ce5




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
        context.secret_key = generate_random_key()
        context.secret_lock = hash256(context.secret_key)
        context.now = datetime.datetime.now()
        context.created_at = int(context.now.timestamp())
        context.email_address = ""
        context.sender_address_non_local = ""

        swap_info = AtomicSwapInfo()
        swap_info.swap_id = context.swap_id
        swap_info.is_closed = False
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
    # @test
    # def test_swap_init_success(self):
    #     # Bob init
    #
    #     context = self.get_context()
    #     init_data = {
    #         "receiver_address": self.account_address2,
    #         "sender_address_non_local": context.sender_address_non_local,
    #         "amount": context.AMOUNT,
    #         "swap_id": context.swap_id,
    #         "secret_lock_optional_bob": context.secret_lock,
    #         "email_address_encrypted_optional_alice": context.email_address,
    #         "created_at": context.created_at,
    #     }
    #
    #     context.client.swap_init(get_swap_init_payload(init_data))
    #
    #     self.expect_get({context.swap_address: None})
    #
    #     self.expect_get({
    #         _make_settings_key(SETTINGS_SWAP_COMMISSION):
    #             get_setting_from_key_value(SETTINGS_SWAP_COMMISSION, context.COMMISSION)
    #     })
    #
    #     TOTAL_TRANSFERED = context.AMOUNT+context.COMMISSION
    #     self.expect_get({self.account_address1: TokenClient.get_account_model(TOTAL_TRANSFERED)})
    #
    #     updated_state = self.transfer(self.account_address1, TOTAL_TRANSFERED, ZERO_ADDRESS, 0, TOTAL_TRANSFERED)
    #
    #     self.expect_set({
    #         **{context.swap_address: context.swap_info},
    #         **updated_state
    #     })
    #
    #     self.expect_ok()
    #
    # @test
    # def test_swap_init_fail_swap_exists(self):
    #     context = self.get_context()
    #     init_data = {
    #         "receiver_address": self.account_address2,
    #         "sender_address_non_local": context.sender_address_non_local,
    #         "amount": context.AMOUNT,
    #         "swap_id": context.swap_id,
    #         "secret_lock_optional_bob": context.secret_lock,
    #         "email_address_encrypted_optional_alice": context.email_address,
    #         "created_at": context.created_at,
    #     }
    #
    #     context.client.swap_init(get_swap_init_payload(init_data))
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_init_fail_created_long_time_ago(self):
    #     context = self.get_context()
    #     init_data = {
    #         "receiver_address": self.account_address2,
    #         "sender_address_non_local": context.sender_address_non_local,
    #         "amount": context.AMOUNT,
    #         "swap_id": context.swap_id,
    #         "secret_lock_optional_bob": context.secret_lock,
    #         "email_address_encrypted_optional_alice": context.email_address,
    #         "created_at": int((datetime.datetime.now() - datetime.timedelta(days=2)).timestamp()),
    #     }
    #
    #     context.client.swap_init(get_swap_init_payload(init_data))
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_init_fail_wrong_receiver_address(self):
    #     context = self.get_context()
    #     init_data = {
    #         "receiver_address": context.swap_address,
    #         "sender_address_non_local": context.sender_address_non_local,
    #         "amount": context.AMOUNT,
    #         "swap_id": context.swap_id,
    #         "secret_lock_optional_bob": context.secret_lock,
    #         "email_address_encrypted_optional_alice": context.email_address,
    #         "created_at": int((datetime.datetime.now() - datetime.timedelta(days=2)).timestamp()),
    #     }
    #
    #     context.client.swap_init(get_swap_init_payload(init_data))
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()

    # END TEST

    # TEST: CLOSE

    # @test
    # def test_swap_close_success(self):
    #     context = self.get_context()
    #     close_data = {
    #         "swap_id": context.swap_id,
    #         "secret_key": context.secret_key
    #     }
    #
    #     context.client.swap_close(get_swap_close_payload(close_data), context.swap_info.receiver_address)
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #     updated_state = self.transfer(ZERO_ADDRESS, context.AMOUNT, self.account_address2, 0, context.AMOUNT)
    #
    #     swap_info = context.swap_info
    #     swap_info.is_closed = True
    #
    #     self.expect_set({
    #         **{context.swap_address: swap_info},
    #         **updated_state
    #     })
    #
    #     self.expect_ok()
    #
    # @test
    # def test_swap_close_fail_no_secret_lock(self):
    #     context = self.get_context()
    #     close_data = {
    #         "swap_id": context.swap_id,
    #         "secret_key": context.secret_key
    #     }
    #
    #     context.client.swap_close(get_swap_close_payload(close_data), context.swap_info.receiver_address)
    #
    #     context.swap_info.secret_lock = ""
    #     self.expect_get({context.swap_address: context.swap_info})
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_close_fail_wrong_secret_key(self):
    #     context = self.get_context()
    #     close_data = {
    #         "swap_id": context.swap_id,
    #         "secret_key": context.secret_key[:-1] + '1'
    #     }
    #
    #     context.client.swap_close(get_swap_close_payload(close_data), context.swap_info.receiver_address)
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_close_fail_not_approved(self):
    #     context = self.get_context()
    #     close_data = {
    #         "swap_id": context.swap_id,
    #         "secret_key": context.secret_key
    #     }
    #
    #     context.client.swap_close(get_swap_close_payload(close_data), context.swap_info.receiver_address)
    #
    #     context.swap_info.is_approved = False
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()

    # END TEST

    # TEST: APPROVE

    # @test
    # def test_swap_approve_success(self):
    #     context = self.get_context()
    #     approve_data = {
    #         "swap_id": context.swap_id,
    #     }
    #
    #     context.client.swap_approve(get_swap_approve_payload(approve_data))
    #
    #     context.swap_info.is_initiator = True
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #     context.swap_info.is_approved = True
    #
    #     self.expect_set({context.swap_address: context.swap_info})
    #
    #     self.expect_ok()
    # #
    # @test
    # def test_swap_approve_fail_not_initiator(self):
    #     context = self.get_context()
    #     approve_data = {
    #         "swap_id": context.swap_id,
    #     }
    #
    #     context.client.swap_approve(get_swap_approve_payload(approve_data))
    #
    #     context.swap_info.is_initiator = False
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_approve_fail_no_secret_lock(self):
    #     context = self.get_context()
    #     approve_data = {
    #         "swap_id": context.swap_id,
    #     }
    #
    #     context.client.swap_approve(get_swap_approve_payload(approve_data))
    #
    #     context.swap_info.is_initiator = True
    #     context.swap_info.secret_lock = ""
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()
    #
    # @test
    # def test_swap_approve_fail_is_closed(self):
    #     context = self.get_context()
    #     approve_data = {
    #         "swap_id": context.swap_id,
    #     }
    #
    #     context.client.swap_approve(get_swap_approve_payload(approve_data))
    #
    #     context.swap_info.is_closed = True
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     self.expect_invalid_transaction()

    # END TEST

    # TEST: EXPIRE

    # @test
    # def test_swap_expire_success_initiator(self):
    #     context = self.get_context()
    #     expire_data = {
    #         "swap_id": context.swap_id,
    #     }
    #
    #     context.client.swap_expire(get_swap_expire_payload(expire_data))
    #
    #     context.swap_info.created_at = int((datetime.datetime.utcnow() - datetime.timedelta(days=1, minutes=1)).timestamp()),
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #
    #     updated_state = self.transfer(ZERO_ADDRESS, context.amount, self.account_address1, 0, context.amount)
    #     context.swap_info.is_closed = True
    #
    #     self.expect_set({
    #         **{context.swap_address: context.swap_info},
    #         **updated_state
    #     })
    #
    #     self.expect_ok()

    # END TEST

    # TEST: SET-LOCK

    # @test
    # def test_swap_set_lock_success(self):
    #     context = self.get_context()
    #     set_secert_lock_data = {
    #         "swap_id": context.swap_id,
    #         "secret_lock": context.secret_lock,
    #     }
    #
    #     context.client.swap_set_secret_lock(get_swap_set_secret_lock_payload(set_secert_lock_data))
    #
    #     context.swap_info.secret_lock = ""
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #     context.swap_info.secret_lock = context.secret_lock
    #
    #     self.expect_set({context.swap_address: context.swap_info})
    #
    #     self.expect_ok()
    #
    # @test
    # def test_swap_set_lock_fail_already_set(self):
    #     context = self.get_context()
    #     set_secert_lock_data = {
    #         "swap_id": context.swap_id,
    #         "secret_lock": context.secret_lock,
    #     }
    #
    #     context.client.swap_set_secret_lock(get_swap_set_secret_lock_payload(set_secert_lock_data))
    #
    #     context.swap_info.secret_lock = context.secret_lock
    #
    #     self.expect_get({context.swap_address: context.swap_info})
    #     self.expect_invalid_transaction()

    # END TEST