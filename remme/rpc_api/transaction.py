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
import logging
from contextlib import suppress

from aiohttp_json_rpc import (
    RpcGenericServerDefinedError,
    RpcInvalidParamsError,
)
from google.protobuf.message import DecodeError
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction, TransactionHeader
)

from remme.shared.exceptions import ClientException, KeyNotFound
from remme.clients.account import AccountClient
from remme.clients.pub_key import PubKeyClient


__all__ = (
    'send_raw_transaction',
    'send_tokens',
    'get_batch_status',

    'list_receipts',
    'list_batches',
    'list_transactions',

    'fetch_batch',
    'fetch_transaction',
)

logger = logging.getLogger(__name__)


async def send_tokens(request):
    try:
        amount = request.params['amount']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed amount')
    try:
        public_key_to = request.params['public_key_to']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_to')
    client = AccountClient()
    signer_account = client.get_account(client.get_signer_address())
    if not amount:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Could not transfer with zero amount'
        )
    if signer_account.balance < amount:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Not enough transferable balance of sender'
        )
    address_to = client.make_address_from_data(public_key_to)
    result = client.transfer(address_to, amount)
    return result['data']


async def send_raw_transaction(request):
    try:
        data = request.params['data']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed data')

    with suppress(Exception):
        data = data.encode('utf-8')

    try:
        transaction = base64.b64decode(data)
    except Exception:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Decode payload of tranasaction failed'
        )

    try:
        tr_pb = Transaction()
        tr_pb.ParseFromString(transaction)
    except DecodeError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Failed to parse transaction proto'
        )

    try:
        tr_head_pb = TransactionHeader()
        tr_head_pb.ParseFromString(tr_pb.header)
    except DecodeError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Failed to parse transaction head proto'
        )

    prefix, public_key = tr_head_pb.signer_public_key[:2], \
        tr_head_pb.signer_public_key[2:]
    if prefix in ('02', '03') and len(public_key) != 64:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Signer public key format is not valid'
        )

    client = PubKeyClient()
    try:
        response = client.send_raw_transaction(tr_pb)
        return response['data']
    except Exception as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Send batch with transaction failed: {e}'
        )


async def list_receipts(request):
    client = AccountClient()
    try:
        ids = request.params['ids']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed ids')
    try:
        return client.list_receipts(ids)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Transactions with ids "{ids}" not found'
        )


async def list_batches(request):
    client = AccountClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')
    try:
        return client.list_batches(ids, start, limit, head, reverse)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )


async def fetch_batch(request):
    try:
        id = request.params['id']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed id')

    client = AccountClient()
    try:
        return client.fetch_batch(id)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Batch with id "{id}" not found'
        )


async def get_batch_status(request):
    try:
        id = request.params['id']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed id')

    client = AccountClient()
    try:
        return client.get_batch_status(id)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )


async def list_transactions(request):
    client = AccountClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')
    try:
        return client.list_transactions(ids, start, limit, head, reverse)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )


async def fetch_transaction(request):
    try:
        id = request.params['id']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed id')

    client = AccountClient()
    try:
        return client.fetch_transaction(id)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Transaction with id "{id}" not found'
        )
