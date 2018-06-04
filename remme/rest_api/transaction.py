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
import base64
from contextlib import suppress

from google.protobuf.message import DecodeError
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from remme.shared.utils import get_batch_id
from remme.certificate.client import CertificateClient


def post(payload):
    tr = payload['transaction']
    with suppress(Exception):
        tr = tr.encode('utf-8')

    try:
        transaction = base64.b64decode(tr)
    except Exception:
        return {'error': 'Decode payload of tranasaction failed'}, 400

    try:
        tr_pb = Transaction()
        tr_pb.ParseFromString(transaction)
    except DecodeError:
        return {'error': 'Failed to parse transaction proto'}, 400

    client = CertificateClient()
    try:
        result = client._send_raw_transaction(tr_pb)
        return {'batch_id': result['batch_id']}, 200
    except Exception as e:
        return {'error': 'Send batch with transaction failed: %s' % e}, 400
