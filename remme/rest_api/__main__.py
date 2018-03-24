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
from flask import Flask
from flask_restful import Resource, Api, reqparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from remme.token.token_client import TokenClient
from remme.certificate.certificate_client import CertificateClient
from remme.shared.exceptions import KeyNotFound
from flask_restful_swagger import swagger

app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1', api_spec_url="/api")


class Token(Resource):
    @swagger.operation(
        notes="""Get balance: </br>
            returns {</br>
                'balance': "10000"</br>
            }""",
        parameters=[
            {
                "name": "pubkey",
                "description": "Key to get balance",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            }
        ]
    )
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('pubkey', required=True)
        arguments = parser.parse_args()
        client = TokenClient()
        address = client.make_address_from_data(arguments.pubkey)
        print('Reading from address: {}'.format(address))
        try:
            balance = client.get_balance(address)
            return {'balance': balance}
        except KeyNotFound:
            return {'error': 'Key not found'}, 404

    @swagger.operation(
        notes="""Transfer tokens: </br>
                returns {</br>
                    'result': "information about successful transaction."</br>
                }""",
        parameters=[
            {
                "name": "pubkey_to",
                "description": "Receiver address",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            },
            {
                "name": "amount",
                "description": "Amount to transfer",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            }
        ]
    )
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('pubkey_to', required=True)
        parser.add_argument('amount', type=int, required=True)
        arguments = parser.parse_args()
        client = TokenClient()
        address_to = client.make_address_from_data(arguments.pubkey_to)
        result = client.transfer(address_to, arguments.amount)
        return result


class Certificate(Resource):
    @swagger.operation(
        notes="""Get certificate status: </br>
                    returns { </br>
                        'revoked': "Bool value", </br>
                        'owner': "Owner's address" </br>
                    }""",
        parameters=[
            {
                "name": "crt_hash",
                "description": "Certificate hash",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            }
        ]
    )
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('crt_hash', required=True)
        arguments = parser.parse_args()
        client = CertificateClient()
        address = client.make_address(arguments.crt_hash)
        try:
            certificate_data = client.get_status(address)
            return {'revoked': certificate_data.revoked,
                    'owner': certificate_data.owner}
        except KeyNotFound:
            return {'error': 'No certificate found'}, 404

    @swagger.operation(
        notes="""Generate certificate: </br>
                        returns { </br>
                            'crt_hash': "Certificate hash", </br>
                            'private_key': "Private key" </br>
                            'status_link': "Transaction status link" </br>
                        }""",
        parameters=[
            {
                "name": "country_name (2 symbols, ex. 'UA')",
                "description": "Country name",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            },
            {
                "name": "state_name",
                "description": "State name",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            },
            {
                "name": "locality_name",
                "description": "Locality name",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            },
            {
                "name": "common_name",
                "description": "Common name",
                "required": True,
                "dataType": "string",
                "paramType": "json"
            },
            {
                "name": "validity",
                "description": "Amount of days certificate is valid",
                "required": True,
                "dataType": "int",
                "paramType": "json"
            },
            {
                "name": "passphrase",
                "description": "passphrase as a second factor encryption",
                "required": False,
                "dataType": "string",
                "paramType": "json"
            }
        ]
    )
    def post(self):
        client = CertificateClient()

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('country_name', required=True)
        parser.add_argument('state_name', required=True)
        parser.add_argument('locality_name', required=True)
        parser.add_argument('common_name', required=True)
        parser.add_argument('validity', type=int, required=True)
        parser.add_argument('passphrase')

        arguments = parser.parse_args()

        encryption_algorithm = None
        if hasattr(arguments, 'passphrase'):
            if arguments.passphrase:
                encryption_algorithm = serialization.BestAvailableEncryption(
                    arguments.passphrase.encode('utf-8'))
            else:
                encryption_algorithm = serialization.NoEncryption()

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        key_export = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption_algorithm,
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, arguments.country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, arguments.state_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, arguments.locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'REMME'),
            x509.NameAttribute(NameOID.COMMON_NAME, arguments.common_name),
            x509.NameAttribute(NameOID.USER_ID, client.get_signer_pubkey())
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
            datetime.datetime.utcnow() + datetime.timedelta(days=arguments.validity)
        ).sign(key, hashes.SHA256(), default_backend())

        crt_export = cert.public_bytes(serialization.Encoding.PEM)

        crt_bin = cert.public_bytes(serialization.Encoding.DER).hex()
        crt_hash = hashlib.sha512(crt_bin.encode('utf-8')).hexdigest()
        rem_sig = client.sign_text(crt_hash)

        crt_sig = key.sign(
            bytes.fromhex(rem_sig),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        status, _ = client.store_certificate(crt_bin, rem_sig, crt_sig.hex())

        return {'certificate': crt_export.decode('utf-8'),
                'private': key_export.decode('utf-8'),
                'status_link': status['link']}

    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('crt_hash', required=True)
        arguments = parser.parse_args()
        client = CertificateClient()
        address = client.make_address(arguments.crt_hash)
        try:
            certificate_data = client.get_status(address)
            if certificate_data.revoked:
                return {'error': 'The certificate was already revoked'}, 405
            client.revoke_certificate(address)
            return {}
        except KeyNotFound:
            return {'error': 'No certificate found'}, 404


api.add_resource(Token, '/token')
api.add_resource(Certificate, '/certificate')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
