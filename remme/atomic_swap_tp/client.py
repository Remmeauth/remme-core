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

import json
import datetime

from remme.protos.atomic_swap_pb2 import AtomicSwapInitPayload, AtomicSwapExpirePayload, AtomicSwapClosePayload, \
    AtomicSwapMethod
from remme.protos.certificate_pb2 import NewCertificatePayload, CertificateMethod
from remme.shared.basic_client import BasicClient
from remme.certificate_tp.handler import CertificateHandler


def get_swap_init_payload(self, receiver_address, sender_address_non_local, amount, swap_id,
                          secret_lock_optional_bob, email_address_encrypted_optional_alice, timestamp):
    payload = AtomicSwapInitPayload()
    payload.receiver_address = receiver_address
    payload.sender_address_non_local = sender_address_non_local
    payload.amount = amount
    payload.swap_id = swap_id
    payload.secret_lock_optional_bob = secret_lock_optional_bob
    payload.email_address_encrypted_optional_alice = email_address_encrypted_optional_alice
    payload.timestamp = timestamp

    return payload

def get_swap_approve_payload(swap_id):
    payload = AtomicSwapInitPayload()
    payload.swap_id = swap_id

    return payload


def get_swap_expire_payload(swap_id):
    payload = AtomicSwapExpirePayload()
    payload.swap_id = swap_id

    return payload


def get_swap_set_secret_lock_payload(swap_id, secret_lock):
    payload = AtomicSwapExpirePayload()
    payload.swap_id = swap_id
    payload.secret_lock = secret_lock

    return payload


def get_swap_close_payload(swap_id, secret_key):
    payload = AtomicSwapClosePayload()
    payload.swap_id = swap_id
    payload.secret_key = secret_key

    return payload


class AtomicSwapClient(BasicClient):
    def __init__(self):
        super().__init__(CertificateHandler)


    def swap_init(self, swap_init_payload):
        return self._send_transaction(AtomicSwapMethod.INIT, swap_init_payload, [self.make_address(swap_init_payload.swap_id)])

    def swap_approve(self, swap_approve_payload):
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload, [self.make_address(swap_approve_payload.swap_id)])

    def swap_expire(self, swap_approve_payload):
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload, [self.make_address(swap_approve_payload.swap_id)])

    def swap_set_secret_lock(self, swap_approve_payload):
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload, [self.make_address(swap_approve_payload.swap_id)])

    def swap_set_secret_lock(self, swap_approve_payload):
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload, [self.make_address(swap_approve_payload.swap_id)])
