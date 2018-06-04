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

from glob import glob
import os
import re
from connexion import NoContent
from sawtooth_signing import create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError

from remme.settings import KEY_DIR


def search():
    keys = []
    for file in glob(f'{KEY_DIR}/*.priv'):
        try:
            with open(file) as f:
                contents = f.read().strip()
                private_key = Secp256k1PrivateKey.from_hex(contents)
                context = create_context('secp256k1')
                signer = CryptoFactory(context).new_signer(private_key)
                keys.append({'name': os.path.splitext(os.path.basename(file))[0],
                             'pub_key': signer.get_public_key().as_hex()})
        except OSError:
            return {'error': f'Cannot read private key file {file}'}, 400
        except ParseError:
            return {'error': f'Cannot parse contents of private key file {file}'}, 400
    return {'keys': keys}


def put(payload):
    name = payload['name']
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    public_key = context.get_public_key(private_key)
    private_key_filename = '{}/{}.priv'.format(KEY_DIR, name)
    public_key_filename = '{}/{}.pub'.format(KEY_DIR, name)
    if os.path.exists(private_key_filename) or os.path.exists(public_key_filename):
        return NoContent, 409
    with open(private_key_filename, mode='w') as private_key_file:
        private_key_file.write(private_key.as_hex())
    with open(public_key_filename, mode='w') as public_key_file:
        public_key_file.write(public_key.as_hex())
    return {'name': name,
            'pub_key': public_key.as_hex()}


def delete(payload):
    name = payload['name']
    private_key_filename = '{}/{}.priv'.format(KEY_DIR, name)
    public_key_filename = '{}/{}.pub'.format(KEY_DIR, name)
    if not (os.path.exists(private_key_filename) or os.path.exists(public_key_filename)):
        return NoContent, 404
    if os.path.exists(private_key_filename):
        os.remove(private_key_filename)
    if os.path.exists(public_key_filename):
        os.remove(public_key_filename)
    return NoContent
