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

import argparse
import hashlib
import time
from processor.protos.token_pb2 import Genesis, TokenPayload
from processor.token.token_handler import TokenHandler
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from processor.shared.exceptions import ClientException
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing import create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from processor.settings import PUB_KEY_FILE, PRIV_KEY_FILE

# HOW TO RUN
# 1. In shell generate needed key `sawtooth keygen key`
# 2. python3 genesis/generate_token_genesis.py <token supply>
from processor.processor.shared.basic_client import _sha512

OUTPUT_SH = 'genesis/token-proposal.sh'
OUTPUT_BATCH = '/root/genesis/token-proposal.batch'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File with a public key to assign initial supply.')
    parser.add_argument('token_supply')
    args = parser.parse_args()

    genesis = Genesis()
    genesis.total_supply = int(args.token_supply)

    payload = TokenPayload()
    payload.method = TokenPayload.GENESIS
    payload.data = genesis.SerializeToString()

    handler = TokenHandler()

    try:
        with open(PRIV_KEY_FILE) as fd:
            private_key_str = fd.read().strip()
            fd.close()
    except OSError as err:
        raise ClientException(
            'Failed to read private key: {}'.format(str(err)))

    try:
        private_key = Secp256k1PrivateKey.from_hex(private_key_str)
    except ParseError as e:
        raise ClientException(
            'Unable to load private key: {}'.format(str(e)))

    signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

    zero_address = handler.namespaces[-1] + '0' * 64
    target_address = handler.make_address(signer.get_public_key().as_hex())

    addresses_input_output = [zero_address, target_address]

    transaction_header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name=handler.family_name,
        family_version=handler.family_versions[-1],
        inputs=addresses_input_output,
        outputs=addresses_input_output,
        dependencies=[],
        payload_sha512=_sha512(payload.SerializeToString()),
        batcher_public_key=signer.get_public_key().as_hex(),
        nonce=time.time().hex().encode()
    ).SerializeToString()

    transaction_signature = signer.sign(transaction_header)

    transaction = Transaction(
        header=transaction_header,
        payload=payload.SerializeToString(),
        header_signature=transaction_signature
    )

    batch_header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=[transaction_signature]
    ).SerializeToString()

    batch_signature = signer.sign(batch_header)

    batch = Batch(
        header=batch_header,
        transactions=[transaction],
        header_signature=batch_signature)

    batch_list = BatchList(batches=[batch])

    batch_file = open(OUTPUT_BATCH, 'wb')
    batch_file.write(batch_list.SerializeToString())
    batch_file.close()
