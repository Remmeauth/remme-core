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
import json

from google.protobuf.text_format import ParseError
from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from remme.protos.transaction_pb2 import TransactionPayload

from remme.shared.utils import hash512, Singleton, from_proto_to_dict


LOGGER = logging.getLogger(__name__)

# Key flag for transaction processor to emit event
EMIT_EVENT = 'emit_event'
PB_CLASS = 'pb_class'
PROCESSOR = 'processor'


def is_address(address):
    try:
        assert isinstance(address, str)
        assert len(address) == 70
        int(address, 16)
        return True
    except (AssertionError, ValueError):
        return False


def add_event(context, event_type, attributes):
    context.add_event(
        event_type=event_type,
        attributes=attributes)


def get_event_attributes(updated_state, header_signature):
    entities_changed_list = [{**{
                                    'address': key,
                                    'type': value.__class__.__name__
                                 },
                              **from_proto_to_dict(value)}
                              for key, value in updated_state.items()]
    content_dict = {"entities_changed": json.dumps(entities_changed_list),
                    "header_signature": header_signature}
    return [(key, str(value)) for key, value in content_dict.items()]

def get_data(context, pb_class, address):
    raw_data = context.get_state([address])
    LOGGER.debug(f'Raw data: {raw_data}')
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


def get_multiple_data(context, data):
    raw_data = context.get_state([el[0] for el in data])
    raw_data = {entry.address: entry.data for entry in raw_data}
    datas = []
    for address, pb_class in data:
        try:
            data = pb_class()
            data.ParseFromString(raw_data[address])
            datas.append(data)
        except Exception:
            datas.append(None)
    return datas


class BasicHandler(metaclass=Singleton):
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
            data_pb = state_processor[transaction_payload.method][PB_CLASS]()
            data_pb.ParseFromString(transaction_payload.data)
            processor = state_processor[transaction_payload.method][PROCESSOR]
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

        event_name = state_processor[transaction_payload.method].get(EMIT_EVENT, None)
        if event_name:
            add_event(context, event_name,
                      get_event_attributes(updated_state, transaction.signature))

    def make_address(self, appendix):
        address = self._prefix + appendix
        if not is_address(address):
            raise InternalError('{} is not a valid address'.format(address))
        return address

    def make_address_from_data(self, data):
        appendix = hash512(data)[:64]
        return self.make_address(appendix)
