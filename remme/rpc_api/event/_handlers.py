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

import uuid
import logging
import json
import abc
import hashlib
import re

from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest
from sawtooth_sdk.protobuf.events_pb2 import EventSubscription, EventList, Event
from sawtooth_sdk.protobuf.validator_pb2 import Message

from remme.shared.exceptions import ClientException
from remme.shared.constants import Events

LOGGER = logging.getLogger(__name__)

BATCH_ID_REGEXP = BLOCK_ID_REGEXP = re.compile(r'[0-9a-f]{128}')
ADDRESS_REGEXP = re.compile(r'[0-9a-f]{70}')
SWAP_ID_REGEXP = re.compile(r'[0-9a-f]{64}')

EVENT_HANDLERS = {}


def register(handler):
    EVENT_HANDLERS[handler.NAME] = handler()
    return handler


def _create_event_payload(event_type, attributes):
    return EventList(
        events=[Event(
            event_type=Events.REMME_BATCH_DELTA.value,
            attributes=[
                Event.Attribute(key=attr_k, value=attr_v)
                for attr_k, attr_v in attributes.items()]
        )]
    )


class BaseEventHandler(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def NAME(cls):
        """Name of event for handler
        """

    @abc.abstractproperty
    def EVENTS(cls):
        """Names of event for parsing
        """

    @abc.abstractmethod
    def parse_evt(self, evt):
        """Parse a required data from the event and return dict
        """

    @abc.abstractmethod
    def prepare_response(self, state, validated_data):
        """Prepare required dictionary on None for the response to client
        """

    @abc.abstractmethod
    def validate(self, msg_id, params):
        """Validate required request params
        """

    @abc.abstractclassmethod
    def hash_keys(cls):
        """Keys from state to create a unique hash
        """

    async def produce_custom_msg(self, stream, validated_data):
        """Produce custom events that sawtooth does not have implementation
        """
        pass

    @classmethod
    def prepare_evt_hash(cls, response):
        hstr = '-'.join((str(response[key]) for key in cls.hash_keys()))
        return hashlib.sha256(f'{cls.NAME}:{hstr}'.encode("utf-8")).hexdigest()

    @classmethod
    def prepare_subscribe_message(cls, event_types, from_block=None):
        last_known_block_ids = [from_block] if from_block else []
        LOGGER.debug(f'last_known_block_ids {last_known_block_ids}')
        return cls._create_subscribe_request(event_types, last_known_block_ids)

    @classmethod
    def _create_subscriptions(cls, event_types):
        return [EventSubscription(event_type=event_name)
                for event_name in cls._prepare_events(event_types)]

    @classmethod
    def _create_subscribe_request(cls, event_types, last_known_block_ids):
        return ClientEventsSubscribeRequest(
            subscriptions=cls._create_subscriptions(event_types),
            last_known_block_ids=last_known_block_ids)

    @classmethod
    def _prepare_events(cls, event_types):
        for event_type in event_types:
            instance = EVENT_HANDLERS.get(event_type)
            if not instance:
                continue
            yield from instance.EVENTS


@register
class BlockEventHandler(BaseEventHandler):

    NAME = 'blocks'
    EVENTS = (
        Events.SAWTOOTH_BLOCK_COMMIT.value,
    )

    @classmethod
    def hash_keys(cls):
        return ('id',)

    def prepare_response(self, state, validated_data):
        return {'id': state}

    def parse_evt(self, evt):
        try:
            return next(filter(lambda el: el['key'] == 'block_id', evt['attributes']))['value']
        except StopIteration:
            pass

    def validate(self, msg_id, params):
        return {}


@register
class BatchEventHandler(BaseEventHandler):

    NAME = 'batch'
    EVENTS = (
        Events.REMME_BATCH_DELTA.value,
    )

    @classmethod
    def hash_keys(cls):
        return ('id', 'status')

    def prepare_response(self, state, validated_data):
        return state

    def parse_evt(self, evt):
        return {evt['key']: evt['value'] for evt in evt['attributes']}

    def validate(self, msg_id, params):
        try:
            batch_id = params['id']

        except KeyError:
            raise RpcInvalidParamsError(message='Missed id', msg_id=msg_id)

        if not BATCH_ID_REGEXP.match(batch_id):
            raise RpcInvalidParamsError(message='Incorrect batch identifier.', msg_id=msg_id)

        return {
            'id': batch_id,
        }

    async def produce_custom_msg(self, stream, validated_data):
        batch_id = validated_data['id']
        router = stream.router
        try:
            result = await router.list_statuses([batch_id])
        except Exception as e:
            LOGGER.warning(f'Error during fetch: {e}')
            return

        data = result['data'][0]
        resp = {
            'id': batch_id,
            'status': data['status'],
        }
        try:
            error = data['invalid_transactions'][0]['message']
            resp['error'] = error
        except (KeyError, IndexError):
            pass

        evt_resp = _create_event_payload(Events.REMME_BATCH_DELTA.value, resp)
        correlation_id = uuid.uuid4().hex
        msg = Message(
            correlation_id=correlation_id,
            content=evt_resp.SerializeToString(),
            message_type=Message.CLIENT_EVENTS)
        await stream.route_msg(msg)


@register
class TransferEventHandler(BaseEventHandler):

    NAME = 'transfer'
    EVENTS = (
        Events.ACCOUNT_TRANSFER.value,
    )

    @classmethod
    def hash_keys(cls):
        return ('from', 'to')

    def prepare_response(self, state, validated_data):
        sender, receiver = state[0], state[1]
        if any([
            sender['address'] == validated_data['address'],
            receiver['address'] == validated_data['address']
        ]):
            return {
                'from': {
                    'address': sender['address'],
                    'balance': float(sender['balance'])
                },
                'to': {
                    'address': receiver['address'],
                    'balance': float(receiver['balance'])
                },
            }

    def parse_evt(self, evt):
        try:
            return json.loads(next(filter(lambda el: el['key'] == 'entities_changed', evt['attributes']))['value'])
        except StopIteration:
            pass

    def validate(self, msg_id, params):
        try:
            address = params['address']

        except KeyError:
            raise RpcInvalidParamsError(message='Missed address', msg_id=msg_id)

        if not ADDRESS_REGEXP.match(address):
            raise RpcInvalidParamsError(message='Incorrect transfer address.', msg_id=msg_id)

        return {
            'address': address,
        }


@register
class AtomicSwapEventHandler(BaseEventHandler):

    NAME = 'atomic_swap'
    EVENTS = (
        Events.SWAP_INIT.value,
        Events.SWAP_CLOSE.value,
        Events.SWAP_APPROVE.value,
        Events.SWAP_EXPIRE.value,
        Events.SWAP_SET_SECRET_LOCK.value,
    )

    @classmethod
    def hash_keys(cls):
        return ('swap_id', 'state')

    def prepare_response(self, state, validated_data):
        swap_info = next(filter(lambda el: el['type'] == 'AtomicSwapInfo', state))
        LOGGER.debug(f'Parsed swap info: {swap_info}')

        id_ = validated_data.get('id')
        if id_ and id_ != swap_info['swap_id']:
            return
        del swap_info['type']
        return swap_info

    def parse_evt(self, evt):
        try:
            return json.loads(next(filter(lambda el: el['key'] == 'entities_changed', evt['attributes']))['value'])
        except StopIteration:
            pass

    def validate(self, msg_id, params):

        from_block = params.get('from_block')
        swap_id = params.get('id')

        if from_block and not isinstance(from_block, str):
            raise ClientException(message='Invalid "from_block" type', msg_id=swap_id)

        if from_block and not BLOCK_ID_REGEXP.match(from_block):
            raise RpcInvalidParamsError(message='Incorrect atomic swap from block identifier.', msg_id=msg_id)

        if swap_id and not SWAP_ID_REGEXP.match(swap_id):
            raise RpcInvalidParamsError(message='Incorrect atomic swap identifier.', msg_id=msg_id)

        return {
            'from_block': from_block,
            'id': swap_id,
        }


SAWTOOTH_TO_REMME_EVENT = {}

for evt in EVENT_HANDLERS.values():
    for evt_type in evt.EVENTS:
        if evt_type in SAWTOOTH_TO_REMME_EVENT:
            SAWTOOTH_TO_REMME_EVENT[evt_type].add(evt.NAME)
        else:
            SAWTOOTH_TO_REMME_EVENT[evt_type] = {evt.NAME}
