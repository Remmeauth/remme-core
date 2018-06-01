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
from remme.certificate.client import CertificateClient
from remme.certificate.handler import CertificateHandler, CERT_STORE_PRICE
from remme.protos.atomic_swap_pb2 import AtomicSwapMethod, AtomicSwapInfo
from remme.protos.certificate_pb2 import CertificateMethod
from remme.rest_api.certificate import get_certificate_signature, get_crt_export_bin_sig_rem_sig
from remme.rest_api.certificate_api_decorator import certificate_put_request, create_certificate
from remme.settings import SETTINGS_SWAP_COMMISSION
from remme.settings.helper import _make_settings_key, get_setting_from_key_value
from remme.shared.logging import test
from remme.shared.utils import generate_random_key, hash256, hash512
from remme.tests.test_helper import HelperTestCase
from remme.account.client import AccountClient
from remme.account.handler import ZERO_ADDRESS
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

LOGGER = logging.getLogger(__name__)


# def get_params():
#     return {
#         'country_name': NameOID.COUNTRY_NAME,
#         'state_name': NameOID.STATE_OR_PROVINCE_NAME,
#         'street_address': NameOID.STREET_ADDRESS,
#         'postal_address': NameOID.POSTAL_ADDRESS,
#         'postal_code': NameOID.POSTAL_CODE,
#         'locality_name': NameOID.LOCALITY_NAME,
#         'common_name': NameOID.COMMON_NAME,
#         'name': NameOID.GIVEN_NAME,
#         'surname': NameOID.SURNAME,
#         'pseudonym': NameOID.PSEUDONYM,
#         'business_category': NameOID.BUSINESS_CATEGORY,
#         'title': NameOID.TITLE,
#         'email': NameOID.EMAIL_ADDRESS,
#         'serial': NameOID.SERIAL_NUMBER,
#         'generation_qualifier': NameOID.GENERATION_QUALIFIER
#     }

class AtomicSwapTestCase(HelperTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(CertificateHandler, CertificateClient)

    def get_context(self):
        context = super().get_context()

        context.certificate_payload = {
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


    @test
    def test_store_success(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.certificate_payload, signer=context.client.get_signer())
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        context.client.store_certificate(crt_bin, rem_sig, crt_sig.hex())
        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        print('certificate address: {}'.format(cert_address))
        self.expect_get({cert_address: None})
        self.expect_get({self.account_address1: AccountClient.get_account_model(CERT_STORE_PRICE)})

        data = CertificateStorage()
        data.hash = fingerprint
        data.owner = signer_pubkey
        data.revoked = False

        account.certificates.append(address)

        self.expect_set({
            self.account_address1: account,
            GENESIS_ADDRESS: genesis_status
        })

        self.expect_ok()
        # def get_new_certificate_payload(self, certificate_raw, signature_rem, signature_crt, cert_signer_public_key):
        #
        # self.send_transaction(CertificateMethod.STORE, CertificateClient.get_new_certificate_payload(TOTAL_SUPPLY),
        #                       [GENESIS_ADDRESS, self.account_address1])
        #
        # self.expect_get({GENESIS_ADDRESS: None})
        #
        # genesis_status = GenesisStatus()
        # genesis_status.status = True
        # account = Account()
        # account.balance = TOTAL_SUPPLY
        #

        #
        # self.expect_ok()

