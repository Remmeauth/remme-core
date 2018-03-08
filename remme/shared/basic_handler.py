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
from google.protobuf.text_format import ParseError
from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.transaction_pb2 import TransactionPayload


def store_state(context, updated_state):
    addresses = context.set_state({k: v.SerializeToString() for k, v in updated_state.items()})
    if len(addresses) < len(updated_state):
        raise InternalError('Failed to update all of states. Updated: {}. Full list of states to update: {}.'
                            .format(addresses, updated_state.keys()))


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


def is_address(address):
    try:
        assert isinstance(address, str)
        assert len(address) == 70
        int(address, 16)
        return True
    except (AssertionError, ValueError):
        return False


class BasicMiddleware:
    def __init__(self, name, versions):
        self._family_name = name
        self._family_versions = versions
        self._prefix = hashlib.sha512(self._family_name.encode('utf-8')).hexdigest()[:6]

    @property
    def family_name(self):
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._prefix]

    def make_address(self, appendix):
        address = self._prefix + appendix
        if not is_address(address):
            raise InternalError('{} is not a valid address'.format(address))
        return address

    def make_address_from_data(self, data):
        appendix = hashlib.sha512(data.encode('utf-8')).hexdigest()[:64]
        return self.make_address(appendix)


class BasicHandler(TransactionHandler):
    def __init__(self, middleware):
        self._middleware = middleware

    @property
    def family_name(self):
        return self._middleware.family_name

    @property
    def family_versions(self):
        return self._middleware.family_versions

    @property
    def namespaces(self):
        return self._middleware.namespaces

    def get_state_processor(self):
        raise InternalError('No implementation for `get_state_processor`')

    def get_message_factory(self, signer=None):
        return MessageFactory(
            family_name=self.family_name,
            family_version=self.family_versions[-1],
            namespace=self.namespaces[-1],
            signer=signer
        )

    def apply(self, transaction, context):
        updated_state = self.process_transaction(context, transaction)
        store_state(context, updated_state)

    def process_transaction(self, context, transaction):
        transaction_payload = TransactionPayload()
        transaction_payload.ParseFromString(transaction.payload)

        state_processor = self.get_state_processor()
        try:
            data_pb = state_processor[transaction_payload.method]['pb_class']()
            data_pb.ParseFromString(transaction_payload.data)
            return state_processor[transaction_payload.method]['processor'](context, transaction.header.signer_public_key, data_pb)
        except KeyError:
            raise InvalidTransaction('Unknown value {} for the certificate operation type.'.
                                     format(int(transaction_payload.method)))
        except ParseError:
            raise InvalidTransaction('Cannot decode transaction payload')
