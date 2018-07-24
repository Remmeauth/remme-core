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

import hashlib

import logging
import os

from google.protobuf.text_format import ParseError
from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512

LOGGER = logging.getLogger(__name__)

# Key flag for transaction processor to emit event
EMIT_EVENT = 'emit_event'


def is_address(address):
    try:
        assert isinstance(address, str)
        assert len(address) == 70
        int(address, 16)
        return True
    except (AssertionError, ValueError):
        return False


def add_event(context, event_type, attributes):
    IS_TESTING = bool(os.getenv('IS_TESTING', default=False))
    if not IS_TESTING:
        LOGGER.info("add_event")
        context.add_event(
            event_type=event_type,
            attributes=[(key, str(value)) for key, value in attributes.items()])


def get_data(context, pb_class, address):
    raw_data = context.get_state([address])
    if raw_data:
        try:
            data = pb_class()
            data.ParseFromString(raw_data[0].data)
            return data
        except IndexError:
            return None
        except ParseError:
            raise InternalError('Failed to deserialize data')
    else:
        return None


class BasicHandler(TransactionHandler):
    """
        BasicHandler contains shared logic...
    """
    def __init__(self, name, versions):
        self._family_name = name
        self._family_versions = versions
        self._prefix = hash512(self._family_name)[:6]

    @property
    def family_name(self):
        """
           BasicHandler contains shared logic...
        """
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._prefix]

    def get_state_processor(self):
        raise InternalError('No implementation for `get_state_processor`')

    def get_message_factory(self, signer=None):
        return MessageFactory(
            family_name=self.family_name,
            family_version=self.family_versions[-1],
            namespace=self.namespaces[-1],
            signer=signer
        )

    def is_handler_address(self, address):
        return is_address(address) and address.startswith(self._prefix)

    def apply(self, transaction, context):
        transaction_payload = TransactionPayload()
        transaction_payload.ParseFromString(transaction.payload)

        state_processor = self.get_state_processor()
        try:
            data_pb = state_processor[transaction_payload.method]['pb_class']()
            data_pb.ParseFromString(transaction_payload.data)
            processor = state_processor[transaction_payload.method]['processor']
            updated_state = processor(context, transaction.header.signer_public_key, data_pb)
        except KeyError:
            raise InvalidTransaction('Unknown value {} for the pub_key operation type.'.
                                     format(int(transaction_payload.method)))
        except ParseError:
            raise InvalidTransaction('Cannot decode transaction payload')

        addresses = context.set_state({k: v.SerializeToString() for k, v in updated_state.items()})
        if len(addresses) < len(updated_state):
            raise InternalError('Failed to update all of states. Updated: {}. '
                                'Full list of states to update: {}.'
                                .format(addresses, updated_state.keys()))

        #TODO add block number
        event_name = state_processor[transaction_payload.method].get(EMIT_EVENT, None)
        if event_name:
            add_event(context, event_name,
                      {"write_addresses": [key for key, _ in updated_state.items()],
                       "family_name": self.family_name,
                       "payload_method": transaction_payload.method})

    def make_address(self, appendix):
        address = self._prefix + appendix
        if not is_address(address):
            raise InternalError('{} is not a valid address'.format(address))
        return address

    def make_address_from_data(self, data):
        appendix = hash512(data)[:64]
        return self.make_address(appendix)
