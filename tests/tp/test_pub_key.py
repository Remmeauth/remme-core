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

from remme.clients.pub_key import PubKeyClient
from remme.tp.pub_key import PubKeyHandler, PUB_KEY_STORE_PRICE, PUB_KEY_MAX_VALIDITY
from remme.protos.pub_key_pb2 import PubKeyStorage, PubKeyMethod
from remme.tp.account import AccountHandler
from remme.rest_api.pub_key import get_crt_export_bin_sig_rem_sig
from remme.rest_api.pub_key_api_decorator import create_certificate
from remme.shared.logging_setup import test
from tests.test_helper import HelperTestCase
from remme.clients.account import AccountClient
from remme.settings.helper import _make_settings_key, get_setting_from_key_value
from remme.settings import SETTINGS_STORAGE_PUB_KEY

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
        cert_address = PubKeyHandler().make_address_from_data(pub_key)

        transaction_signature = None
        if type == 'store':
            transaction_signature = context.client.store_pub_key(pub_key, rem_sig, crt_sig, valid_from, valid_to)
        elif type == 'revoke':
            transaction_signature = context.client.revoke_pub_key(cert_address)
        else:
            raise AssertionError('Type for pre parse not found')

        return transaction_signature, cert_address, transaction_payload

    @test
    def test_store_success(self):
        context = self.get_context()

        cert, key, _ = create_certificate(context.pub_key_payload, signer=context.client.get_signer())

        transaction_signature, cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key)
        crt_export, crt_bin, crt_sig, rem_sig, pub_key, \
            valid_from, valid_to = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        account = AccountClient.get_account_model(PUB_KEY_STORE_PRICE)

        storage_account = AccountClient.get_account_model(0)
        storage_signer = self.get_new_signer()
        storage_pub_key = storage_signer.get_public_key().as_hex()
        storage_address = AccountHandler().make_address_from_data(storage_pub_key)

        data = PubKeyStorage()
        data.owner = self.account_signer1.get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        self.expect_get({cert_address: None, self.account_address1: account})
        self.expect_get({_make_settings_key('remme.economy_enabled'): None})
        self.expect_get({
            _make_settings_key(SETTINGS_STORAGE_PUB_KEY):
                get_setting_from_key_value(SETTINGS_STORAGE_PUB_KEY,
                                           storage_pub_key)
        })
        LOGGER.error(f'a {self.account_address1} b {storage_address} bpk {storage_pub_key}')
        self.expect_get({self.account_address1: account,
                         storage_address: storage_account})

        context.client.store_pub_key(pub_key, rem_sig, crt_sig,
                                     valid_from, valid_to)

        account.balance -= PUB_KEY_STORE_PRICE
        account.pub_keys.append(cert_address)
        storage_account.balance += PUB_KEY_STORE_PRICE

        self.expect_set(transaction_signature, PubKeyMethod.STORE, {
            self.account_address1: account,
            cert_address: data,
            storage_address: storage_account
        })

        self.expect_ok()

    @test
    def test_store_fail_invalid_validity_date(self):
        context = self.get_context()

        cert, key, _ = create_certificate(context.pub_key_payload, signer=context.client.get_signer())
        crt_export, crt_bin, crt_sig, rem_sig, pub_key, \
            valid_from, valid_to = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        cert_address = PubKeyHandler().make_address_from_data(pub_key)

        valid_from = int(valid_from - PUB_KEY_MAX_VALIDITY.total_seconds())
        valid_to = int(valid_to + PUB_KEY_MAX_VALIDITY.total_seconds())

        context.client.store_pub_key(pub_key, rem_sig, crt_sig, valid_from, valid_to)

        self.expect_get({cert_address: None, self.account_address1: None})

        self.expect_invalid_transaction()

    @test
    def test_revoke_success(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.pub_key_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        transaction_signature, cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key, 'revoke')

        data = PubKeyStorage()
        data.owner = context.client.get_signer().get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        self.expect_get({cert_address: data})

        data.revoked = True

        self.expect_set(transaction_signature, PubKeyMethod.REVOKE, {
            cert_address: data
        })

        self.expect_ok()

    @test
    def test_revoke_fail_wrong_signer(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.pub_key_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        signature, cert_address, transaction_payload = self._pre_parse_payload_and_exec(context, cert, key, 'revoke')

        data = PubKeyStorage()
        data.owner = self.account_signer2.get_public_key().as_hex()
        data.payload.CopyFrom(transaction_payload)
        data.revoked = False

        self.expect_get({cert_address: data})

        self.expect_invalid_transaction()
