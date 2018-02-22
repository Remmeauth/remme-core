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

import datetime
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from processor.shared.basic_cli import BasicCli
from processor.certificate.certificate_client import CertificateClient
from processor.shared.exceptions import CliException, KeyNotFound


class CertificateCli(BasicCli):
    def __init__(self):
        self.client = CertificateClient()

    def parser_certificate(self, subparsers, parent_parser):
        message = 'Generate a certificate on the REMME blockchain.'

        subparsers.add_parser(
            'generate',
            parents=[parent_parser],
            description=message,
            help='Generate and register a new certificate.')

    def parser_revoke(self, subparsers, parent_parser):
        message = 'Revoke a certificate on the REMME blockchain.'

        parser = subparsers.add_parser(
            'revoke',
            parents=[parent_parser],
            description=message,
            help='Revoke a certificate.')

        parser.add_argument(
            'address',
            type=str,
        )

    def parser_status(self, subparsers, parent_parser):
        message = 'Check a certificate status.'

        parser = subparsers.add_parser(
            'check',
            parents=[parent_parser],
            description=message,
            help='Check a certificate status..')

        parser.add_argument(
            'address',
            type=str,
        )

    def revoke(self, args):
        self.client.revoke_certificate(args.address)

    def check_status(self, args):
        try:
            status = self.client.get_status(args.address)
            if status:
                print('Certificate on address {} is revoked.'.format(args.address))
            else:
                print('Certificate on address {} is valid.'.format(args.address))
        except KeyNotFound:
            print('No certificate registered on address {}.'.format(args.address))

    def generate_and_register(self, args):
        # GENERATE KEY AND CERTIFICATE
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        with open("key.pem", "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
            ))
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "REMME"),
            x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),
            x509.NameAttribute(NameOID.USER_ID, self.client.get_signer_address())
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            # Our certificate will be valid for 10 days
            datetime.datetime.utcnow() + datetime.timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
            # Sign our certificate with our private key
        ).sign(key, hashes.SHA256(), default_backend())
        # Write our certificate out to disk.
        with open("certificate.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        crt_bin = cert.public_bytes(serialization.Encoding.DER).hex()
        crt_hash = hashlib.sha512(crt_bin.encode('utf-8')).hexdigest()
        rem_sig = self.client.sign_text(crt_hash)

        crt_sig = key.sign(
            bytes.fromhex(rem_sig),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        self.client.register_certificate(crt_bin, rem_sig, crt_sig.hex())

    def run(self):
        commands = [{
            'name': 'generate',
            'parser': self.parser_certificate,
            'action': self.generate_and_register
        }, {
            'name': 'revoke',
            'parser': self.parser_revoke,
            'action': self.revoke
        }, {
            'name': 'check',
            'parser': self.parser_status,
            'action': self.check_status
        }]
        self.main_wrapper(commands)


def main():
    CertificateCli().run()
