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

from remme.clients.pub_key import PubKeyClient
from remme.tp.pub_key import PubKeyHandler, CERT_STORE_PRICE, CERT_MAX_VALIDITY, CERT_MAX_VALIDITY_DAYS
from remme.protos.pub_key_pb2 import PubKeyStorage
from remme.rest_api.pub_key import get_pub_key_signature, get_crt_export_bin_sig_rem_sig
from remme.rest_api.pub_key_api_decorator import pub_key_put_request, create_certificate
from remme.shared.logging import test
from tests.test_helper import HelperTestCase
from remme.clients.account import AccountClient
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

LOGGER = logging.getLogger(__name__)


class PubKeyTestCase(HelperTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass(PubKeyHandler, PubKeyClient)

    def get_context(self):
        context = super().get_context()
        context.pub_key_payload = {
            "business_category": "UA",
            "common_name": "UA",
            "country_name": "UA",
            "email": "UA",
            "generation_qualifier": "UA",
            "locality_name": "UA",
            "name": "UA",
            "passphrase": "UA",
            "postal_address": "UA",
            "postal_code": "UA",
            "pseudonym": "UA",
            "serial": "UA",
            "state_name": "UA",
            "street_address": "UA",
            "surname": "UA",
            "title": "UA",
            "validity": 0,
            "validity_after": 0
        }

        return context

    def _pre_parse_payload_and_exec(self, context, cert, key, type='store'):
        crt_export, crt_bin, crt_sig, rem_sig, pub_key, \
            valid_from, valid_to = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        transaction_payload = context.client.get_new_pub_key_payload(pub_key, rem_sig, crt_sig, valid_from, valid_to)
        cert_address = PubKeyHandler.make_address_from_data(pub_key)

        if type == 'store':
            context.client.store_pub_key(pub_key, rem_sig, crt_sig, valid_from, valid_to)
        elif type == 'revoke':
            context.client.revoke_pub_key(cert_address)
        else:
            raise AssertionError('Type for pre parse not found')

        return cert_address, transaction_payload

    @test
    def test_store_success(self):
        context = self.get_context()

        cert, key, _ = create_certificate(context.pub_key_payload, signer=context.client.get_signer())
        cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key)
        self.expect_get({cert_address: None})

        account = AccountClient.get_account_model(CERT_STORE_PRICE)
        self.expect_get({self.account_address1: account})

        data = PubKeyStorage()
        data.owner = self.account_signer1.get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        account.balance -= CERT_STORE_PRICE
        account.pub_keys.append(cert_address)

        self.expect_set({
            self.account_address1: account,
            cert_address: data
        })

        self.expect_ok()

    @test
    def test_revoke_success(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.pub_key_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key, 'revoke')

        data = PubKeyStorage()
        data.owner = context.client.get_signer().get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        self.expect_get({cert_address: data})

        data.revoked = True

        self.expect_set({
            cert_address: data
        })

        self.expect_ok()

    @test
    def test_revoke_fail_wrong_signer(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.pub_key_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key, 'revoke')

        data = PubKeyStorage()
        data.owner = self.account_signer2.get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        self.expect_get({cert_address: data})

        self.expect_invalid_transaction()
