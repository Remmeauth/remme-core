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

from remme.clients.certificate import CertificateClient
from remme.tp.certificate import CertificateHandler, CERT_STORE_PRICE, CERT_MAX_VALIDITY, CERT_MAX_VALIDITY_DAYS
from remme.protos.certificate_pb2 import CertificateStorage
from remme.rest_api.certificate import get_certificate_signature, get_crt_export_bin_sig_rem_sig
from remme.rest_api.certificate_api_decorator import certificate_put_request, create_certificate
from remme.shared.logging import test
from remme.tests.test_helper import HelperTestCase
from remme.clients.account import AccountClient
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

LOGGER = logging.getLogger(__name__)


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
        self.expect_get({cert_address: None})

        account = AccountClient.get_account_model(CERT_STORE_PRICE)
        self.expect_get({self.account_address1: account})

        certificate = x509.load_der_x509_certificate(bytes.fromhex(crt_bin), default_backend())

        data = CertificateStorage()
        fingerprint = certificate.fingerprint(hashes.SHA512()).hex()[:64]
        data.hash = fingerprint
        data.owner = self.account_signer1.get_public_key().as_hex()
        data.revoked = False

        account.balance -= CERT_STORE_PRICE
        account.certificates.append(cert_address)

        self.expect_set({
            self.account_address1: account,
            cert_address: data
        })

        self.expect_ok()

    @test
    def test_store_fail_invalid_validity_date(self):
        context = self.get_context()

        context.certificate_payload['validity'] = CERT_MAX_VALIDITY_DAYS + 1
        cert, key, key_export = create_certificate(context.certificate_payload, signer=context.client.get_signer())
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)
        context.client.store_certificate(crt_bin, rem_sig, crt_sig.hex())
        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        self.expect_get({cert_address: None})

        self.expect_invalid_transaction()

    @test
    def test_store_fail_invalid_org_name(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.certificate_payload,
                                                   org_name='different',
                                                   signer=context.client.get_signer())
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)
        context.client.store_certificate(crt_bin, rem_sig, crt_sig.hex())
        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        self.expect_get({cert_address: None})

        self.expect_invalid_transaction()

    @test
    def test_store_fail_invalid_signer(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.certificate_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)
        context.client.store_certificate(crt_bin, rem_sig, crt_sig.hex())
        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        self.expect_get({cert_address: None})

        self.expect_invalid_transaction()

    @test
    def test_revoke_success(self):
        context = self.get_context()

        cert, key, key_export = create_certificate(context.certificate_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        context.client.revoke_certificate(cert_address)

        data = CertificateStorage()
        data.owner = context.client.get_signer().get_public_key().as_hex()
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

        cert, key, key_export = create_certificate(context.certificate_payload,
                                                   org_name='different',
                                                   signer=self.account_signer2)
        crt_export, crt_bin, crt_sig, rem_sig = get_crt_export_bin_sig_rem_sig(cert, key, context.client)

        cert_address = CertificateHandler.make_address_from_data(crt_bin)
        context.client.revoke_certificate(cert_address)

        data = CertificateStorage()
        data.owner = self.account_signer2.get_public_key().as_hex()
        data.revoked = False

        self.expect_get({cert_address: data})

        self.expect_invalid_transaction()
