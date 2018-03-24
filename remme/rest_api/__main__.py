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

from flask import Flask
from flask_restful import Resource, Api, reqparse

from remme.token.token_client import TokenClient
from remme.certificate.certificate_client import CertificateClient
from remme.shared.exceptions import KeyNotFound


app = Flask(__name__)
api = Api(app)


class Keys(Resource):
    def get(self):
        pass


class Token(Resource):
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

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        # for future use: multiple keys on a single instance
        parser.add_argument('pubkey_from', required=True)
        parser.add_argument('pubkey_to', required=True)
        parser.add_argument('amount', type=int, required=True)
        arguments = parser.parse_args()
        client = TokenClient()
        address_from = client.make_address_from_data(arguments.pubkey_from)
        address_to = client.make_address_from_data(arguments.pubkey_to)
        result = client.transfer(address_to, arguments.amount)
        return result


class Certificate(Resource):
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
            return {'error': 'No certificate found with hash '.format(arguments.crt_hash)}, 404

    def post(self):
        pass

    def delete(self):
        pass


api.add_resource(Keys, '/keys')
api.add_resource(Token, '/token')
api.add_resource(Certificate, '/certificate')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
