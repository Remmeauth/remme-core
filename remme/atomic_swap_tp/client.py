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

from remme.atomic_swap_tp.handler import AtomicSwapHandler
from remme.protos.atomic_swap_pb2 import AtomicSwapInitPayload, AtomicSwapExpirePayload, AtomicSwapClosePayload, \
    AtomicSwapMethod, AtomicSwapInfo
from remme.protos.certificate_pb2 import NewCertificatePayload, CertificateMethod
from remme.shared.basic_client import BasicClient
from remme.certificate.handler import CertificateHandler
from remme.token_tp.handler import TokenHandler


def get_swap_init_payload(args):
    payload = AtomicSwapInitPayload()
    payload.receiver_address = args.receiver_address
    payload.sender_address_non_local = args.sender_address_non_local
    payload.amount = args.amount
    payload.swap_id = args.swap_id
    payload.secret_lock_optional_bob = args.secret_lock_optional_bob
    payload.email_address_encrypted_optional_alice = args.email_address_encrypted_optional_alice
    payload.timestamp = args.timestamp

    return payload


def get_swap_approve_payload(args):
    payload = AtomicSwapInitPayload()
    payload.swap_id = args.swap_id

    return payload


def get_swap_expire_payload(args):
    payload = AtomicSwapExpirePayload()
    payload.swap_id = args.swap_id

    return payload


def get_swap_set_secret_lock_payload(args):
    payload = AtomicSwapExpirePayload()
    payload.swap_id = args.swap_id
    payload.secret_lock = args.secret_lock

    return payload


def get_swap_close_payload(args):
    payload = AtomicSwapClosePayload()
    payload.swap_id = args.swap_id
    payload.secret_key = args.secret_key

    return payload

# TODO add addresses for transfers
class AtomicSwapClient(BasicClient):
    def __init__(self):
        super().__init__(AtomicSwapHandler)

    def swap_init(self, swap_init_payload):
        return self._send_transaction(AtomicSwapMethod.INIT, swap_init_payload,
                                      [self.make_address(swap_init_payload.swap_id),
                                       self.get_user_address(),
                                       TokenHandler().zero_address])

    def swap_approve(self, swap_approve_payload):
        return self._send_transaction(AtomicSwapMethod.APPROVE, swap_approve_payload,
                                      [self.make_address(swap_approve_payload.swap_id)])

    def swap_expire(self, swap_expire_payload):
        return self._send_transaction(AtomicSwapMethod.EXPIRE, swap_expire_payload,
                                      [self.make_address(swap_expire_payload.swap_id)])

    def swap_set_secret_lock(self, swap_set_secret_lock_payload):
        return self._send_transaction(AtomicSwapMethod.SET_SECRET_LOCK, swap_set_secret_lock_payload,
                                      [self.make_address(swap_set_secret_lock_payload.swap_id)])

    def swap_close(self, swap_close_payload, receiver_address):
        return self._send_transaction(AtomicSwapMethod.CLOSE, swap_close_payload,
                                      [self.make_address(swap_close_payload.swap_id),
                                       receiver_address])

    def swap_get(self, swap_id):
        atomic_swap_info = AtomicSwapInfo()
        atomic_swap_info.ParseFromString(self.get_value(self.make_address(swap_id)))
        return atomic_swap_info
        # return self._send_transaction(AtomicSwapMethod.CLOSE, swap_close_payload,
        #                               [self.make_address(swap_close_payload.swap_id),
        #                                receiver_address])
