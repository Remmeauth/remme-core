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
import hashlib
import base64
import codecs
import re

import sha3
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError
from sawtooth_signing import create_context
from sawtooth_sdk.protobuf import client_list_control_pb2
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.block_pb2 import BlockHeader
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

from remme.shared import exceptions as errors
from remme.protos.consensus_messages_pb2 import ConsensusSeal


LOGGER = logging.getLogger(__name__)


def generate_random_key():
    return create_context('secp256k1').new_random_private_key().as_hex()


# kecak256
def hash256(data):
    return hashlib.sha3_256(data.encode('utf-8')
                            if isinstance(data, str) else data).hexdigest()


def hash512(data):
    return hashlib.sha512(data.encode('utf-8')
                          if isinstance(data, str) else data).hexdigest()


def remove_0x_prefix(value):
    if value.startswith('0x'):
        return value[2:]
    return value


def web3_hash(data):
    if len(data) % 2:
        data = '0x0' + remove_0x_prefix(data)

    data = codecs.decode(remove_0x_prefix(data), 'hex')
    return sha3.keccak_256(data).hexdigest()


def message_to_dict(message):
    """Converts a Protobuf object to a python dict with desired settings.
    """
    return MessageToDict(
        message,
        including_default_value_fields=True,
        preserving_proto_field_name=True)


def expand_batch(batch):
    """Deserializes a Batch's header, and the header of its Transactions.
    """
    parse_header(BatchHeader, batch)
    if 'transactions' in batch:
        batch['transactions'] = [
            expand_transaction(t) for t in batch['transactions']]
    return batch


def parse_consensus(consensus_proto, resource):
    """Deserializes a resource's base64 encoded Protobuf consensus.
    """
    consensus = consensus_proto()
    try:
        consensus_bytes = base64.b64decode(resource['header']['consensus'])
        logging.debug(f"Consensus base64: {resource['header']['consensus']}")
        consensus.ParseFromString(consensus_bytes)
    except (KeyError, TypeError, ValueError, DecodeError):
        pass

    resource['header']['consensus'] = message_to_dict(consensus)
    return resource


def parse_header(header_proto, resource):
    """Deserializes a resource's base64 encoded Protobuf header.
    """
    header = header_proto()
    try:
        header_bytes = base64.b64decode(resource['header'])
        header.ParseFromString(header_bytes)
    except (KeyError, TypeError, ValueError, DecodeError):
        header = resource.get('header', None)
        LOGGER.error(
            'The validator sent a resource with %s %s',
            'a missing header' if header is None else 'an invalid header:',
            header or '')
        raise errors.ResourceHeaderInvalid()

    resource['header'] = message_to_dict(header)
    return resource


def get_head_id(head_id):
    """Fetches the request's head query, and validates if present.
    """
    if head_id is not None:
        validate_id(head_id)

    return head_id


def expand_transaction(transaction):
    """Deserializes a Transaction's header.
    """
    return parse_header(TransactionHeader, transaction)


def validate_id(resource_id):
    """Confirms a header_signature is 128 hex characters, raising an
    ApiError if not.
    """
    if not re.fullmatch('[0-9a-f]{128}', resource_id):
        raise errors.InvalidResourceId(f'Invalid id "{resource_id}"')


def get_filter_ids(id_query):
    """Parses the `id` filter paramter from the url query.
    """

    if id_query is None:
        return None

    filter_ids = id_query.split(',')
    for filter_id in filter_ids:
        validate_id(filter_id)

    return filter_ids


def get_sorting_message(reverse, key):
    """Parses the reverse query into a list of ClientSortControls protobuf
    messages.
    """
    control_list = []
    if reverse is None:
        return control_list

    if reverse.lower() == "":
        control_list.append(client_list_control_pb2.ClientSortControls(
            reverse=True,
            keys=key.split(",")
        ))
    elif reverse.lower() != 'false':
        control_list.append(client_list_control_pb2.ClientSortControls(
            reverse=True,
            keys=reverse.split(",")
        ))

    return control_list


def make_paging_message(controls):
    """Turns a raw paging controls dict into Protobuf ClientPagingControls.
    """

    return client_list_control_pb2.ClientPagingControls(
        start=controls.get('start', None),
        limit=controls.get('limit', None))


def get_paging_controls(start, limit):
    """Parses start and/or limit queries into a paging controls dict.
    """
    controls = {}

    if limit is not None:
        try:
            controls['limit'] = int(limit)
        except ValueError:
            LOGGER.debug('Request query had an invalid limit: %s', limit)
            raise errors.CountInvalid()

        if controls['limit'] <= 0:
            LOGGER.debug('Request query had an invalid limit: %s', limit)
            raise errors.CountInvalid()

    if start is not None:
        controls['start'] = start

    return controls


def expand_block(block):
    """Deserializes a Block's header, and the header of its Batches.
    """
    parse_header(BlockHeader, block)
    parse_consensus(ConsensusSeal, block)
    if 'batches' in block:
        block['batches'] = [expand_batch(b) for b in block['batches']]
    return block


def drop_empty_props(item):
    """Remove properties with empty strings from nested dicts.
    """
    if isinstance(item, list):
        return [drop_empty_props(i) for i in item]
    if isinstance(item, dict):
        return {
            k: drop_empty_props(v)
            for k, v in item.items() if v != ''
        }
    return item


def drop_id_prefixes(item):
    """Rename keys ending in 'id', to just be 'id' for nested dicts.
    """
    if isinstance(item, list):
        return [drop_id_prefixes(i) for i in item]
    if isinstance(item, dict):
        return {
            'id' if k.endswith('id') else k: drop_id_prefixes(v)
            for k, v in item.items()
        }
    return item


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls) \
                .__call__(*args, **kwargs)
        return cls._instances[cls]
