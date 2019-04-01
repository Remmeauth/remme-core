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

from remme.shared.exceptions import KeyNotFound
from remme.tp.basic import PB_CLASS, VALIDATOR
from remme.tp.__main__ import TP_HANDLERS
from remme.clients.account import AccountClient
from remme.clients.pub_key import PubKeyClient
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.forms import (
    BatchIdentifierForm,
    TransactionIdentifierForm,
    IdentifiersForm,
    ProtoForm,
)

from .utils import validate_params


__all__ = (
    'send_raw_transaction',
    'get_batch_status',

    'list_receipts',
    'list_batches',
    'list_transactions',

    'fetch_batch',
    'fetch_transaction',
)

logger = logging.getLogger(__name__)


@validate_params(ProtoForm)
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
    signer_account = await client.get_account(client.get_signer_address())
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
    result = await client.transfer(address_to, amount)
    return result['data']


def _get_proto_validator(current_handler, tr_payload_pb):
    processor = current_handler.get_state_processor()
    try:
        state_processor = processor[tr_payload_pb.method]
    except KeyError:
        logger.debug(f'Payload method "{tr_payload_pb.method}" '
                     f'not found for processor {processor}')
        return

    try:
        pb_class = state_processor[PB_CLASS]
        validator_class = state_processor[VALIDATOR]
    except KeyError:
        logger.debug('"validator_class" or "pb_class" not found '
                     f'in {state_processor}')
        return

    try:
        data_pb = pb_class()
        data_pb.ParseFromString(tr_payload_pb.data)
    except DecodeError:
        logger.debug('Failed to parse payload proto '
                     f'with protobuf "{pb_class}"')
        return

    return validator_class.load_proto(data_pb)


@validate_params(ProtoForm)
async def send_raw_transaction(request):
    try:
        data = request.params['data']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed data')

    try:
        transaction = base64.b64decode(data.encode('utf-8'))
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

    try:
        tr_payload_pb = TransactionPayload()
        tr_payload_pb.ParseFromString(tr_pb.payload)
    except DecodeError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Failed to parse transaction payload proto'
        )

    prefix, public_key = tr_head_pb.signer_public_key[:2], \
        tr_head_pb.signer_public_key[2:]
    if prefix in ('02', '03') and len(public_key) != 64:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Signer public key format is not valid'
        )

    try:
        handler = TP_HANDLERS[tr_head_pb.family_name]
    except KeyError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Validation handler not set for this method'
        )

    validator = _get_proto_validator(handler, tr_payload_pb)
    if validator and not validator.validate():
        logger.debug('Form "send_raw_transaction" validator errors: '
                     f'{validator.errors}')
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Invalid "{validator.get_pb_class().__name__}" '
                    'structure'
        )

    client = PubKeyClient()
    response = await client.send_raw_transaction(tr_pb)
    return response['data']


@validate_params(IdentifiersForm)
async def list_receipts(request):
    ids = request.params['ids']

    client = AccountClient()
    try:
        return await client.list_receipts(ids)
    except KeyNotFound:
        raise KeyNotFound(f'Transactions with ids "{ids}" not found')


@validate_params(ProtoForm, ignore_fields=('ids', 'start', 'limit', 'head', 'reverse'))
async def list_batches(request):
    client = AccountClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    return await client.list_batches(ids, start, limit, head, reverse)


@validate_params(BatchIdentifierForm)
async def fetch_batch(request):
    batch_id = request.params['id']

    client = AccountClient()
    try:
        return await client.fetch_batch(batch_id)
    except KeyNotFound:
        raise KeyNotFound(f'Batch with batch id `{batch_id}` not found.')


@validate_params(BatchIdentifierForm)
async def get_batch_status(request):
    batch_id = request.params['id']

    client = AccountClient()
    return await client.get_batch_status(batch_id)


@validate_params(ProtoForm, ignore_fields=('ids', 'start', 'limit', 'head', 'reverse', 'family_name'))
async def list_transactions(request):
    client = AccountClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')
    family_name = request.params.get('family_name')

    return await client.list_transactions(ids, start, limit, head, reverse, family_name)


@validate_params(TransactionIdentifierForm)
async def fetch_transaction(request):
    id = request.params['id']
    client = AccountClient()
    try:
        return await client.fetch_transaction(id)
    except KeyNotFound:
        raise KeyNotFound(f'Transaction with id "{id}" not found')
