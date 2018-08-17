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

from remme.tp.atomic_swap import AtomicSwapHandler
from remme.protos.atomic_swap_pb2 import AtomicSwapInitPayload, AtomicSwapExpirePayload, AtomicSwapClosePayload, \
    AtomicSwapMethod, AtomicSwapInfo, AtomicSwapSetSecretLockPayload, AtomicSwapApprovePayload
from sawtooth_sdk.protobuf.setting_pb2 import Setting
from remme.settings import SETTINGS_SWAP_COMMISSION, ZERO_ADDRESS, SETTINGS_PUB_KEY_ENCRYPTION
from remme.settings.helper import _make_settings_key
from remme.clients.basic import BasicClient

LOGGER = logging.getLogger(__name__)


def get_swap_init_payload(receiver_address, sender_address_non_local, amount,
                          swap_id, created_at, secret_lock_by_solicitor="",
                          email_address_encrypted_by_initiator=""):
    payload = AtomicSwapInitPayload()
    payload.receiver_address = receiver_address
    payload.sender_address_non_local = sender_address_non_local
    payload.amount = amount
    payload.swap_id = swap_id
    payload.secret_lock_by_solicitor = secret_lock_by_solicitor
    payload.email_address_encrypted_by_initiator = email_address_encrypted_by_initiator
    payload.created_at = created_at

    return payload


def get_swap_approve_payload(swap_id):
    payload = AtomicSwapApprovePayload()
    payload.swap_id = swap_id

    return payload


def get_swap_expire_payload(swap_id):
    payload = AtomicSwapExpirePayload()
    payload.swap_id = swap_id

    return payload


def get_swap_set_secret_lock_payload(swap_id, secret_lock):
    payload = AtomicSwapSetSecretLockPayload()
    payload.swap_id = swap_id
    payload.secret_lock = secret_lock

    return payload


def get_swap_close_payload(swap_id, secret_key):
    payload = AtomicSwapClosePayload()
    payload.swap_id = swap_id
    payload.secret_key = secret_key

    return payload


class AtomicSwapClient(BasicClient):
    def __init__(self, test_helper=None):
        super().__init__(AtomicSwapHandler, test_helper=test_helper)

    def swap_init(self, swap_init_payload):
        addresses_input = [
            self.make_address_from_data(swap_init_payload.swap_id),
            self.get_user_address(),
            _make_settings_key(SETTINGS_SWAP_COMMISSION),
        ]
        addresses_output = [
            self.make_address_from_data(swap_init_payload.swap_id),
            self.get_user_address(),
            ZERO_ADDRESS,
        ]
        return self._send_transaction(AtomicSwapMethod.INIT, swap_init_payload,
                                      addresses_input, addresses_output)

    def swap_approve(self, swap_approve_payload):
        LOGGER.info('swap id: {}'.format(swap_approve_payload.swap_id))
        LOGGER.info('swap payload: {}'.format(swap_approve_payload))
        addresses_input = [
            self.make_address_from_data(swap_approve_payload.swap_id),
            self.get_user_address(),
        ]
        addresses_output = [
            self.make_address_from_data(swap_approve_payload.swap_id),
        ]
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload,
                                      addresses_input, addresses_output)

    def swap_expire(self, swap_expire_payload):
        addresses_input = [
            self.make_address_from_data(swap_expire_payload.swap_id),
            self.get_user_address(),
        ]
        addresses_output = addresses_input
        return self._send_transaction(AtomicSwapMethod.EXPIRE, swap_expire_payload,
                                      addresses_input, addresses_output)

    def swap_set_secret_lock(self, swap_set_secret_lock_payload):
        addresses_input = [
            self.make_address_from_data(swap_set_secret_lock_payload.swap_id),
            self.get_user_address(),
        ]
        addresses_output = [
            self.make_address_from_data(swap_set_secret_lock_payload.swap_id),
        ]
        return self._send_transaction(AtomicSwapMethod.SET_SECRET_LOCK, swap_set_secret_lock_payload,
                                      addresses_input, addresses_output)

    def swap_close(self, swap_close_payload, receiver_address):
        addresses_input = [
            self.make_address_from_data(swap_close_payload.swap_id),
            ZERO_ADDRESS,
            receiver_address,
            self.get_user_address(),
        ]
        addresses_output = addresses_input
        return self._send_transaction(AtomicSwapMethod.CLOSE, swap_close_payload,
                                      addresses_input, addresses_output)

    def swap_get(self, swap_id):
        atomic_swap_info = AtomicSwapInfo()
        atomic_swap_info.ParseFromString(self.get_value(self.make_address_from_data(swap_id)))
        return atomic_swap_info

    def get_pub_key_encryption(self):
        setting = Setting()
        setting.ParseFromString(self.get_value(_make_settings_key(SETTINGS_PUB_KEY_ENCRYPTION)))
        return setting.entries[0].value
