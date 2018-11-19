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
import hashlib
import logging
import asyncio
import weakref
from contextlib import contextmanager, suppress

import aiohttp
from aiohttp import web
from aiohttp_json_rpc.exceptions import (
    RpcMethodNotFoundError,
    RpcInvalidParamsError,
)

from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf.client_event_pb2 import (
    ClientEventsSubscribeRequest,
    ClientEventsSubscribeResponse,
)
from sawtooth_sdk.protobuf.events_pb2 import (
    EventList, Event, EventSubscription,
)

from remme.settings import ZMQ_CONNECTION_TIMEOUT
from remme.shared.utils import message_to_dict
from remme.shared.exceptions import RpcError, ClientException
from remme.shared.messaging import Connection
from remme.shared.router import Router
from remme.shared.constants import Events
from .utils import deserialize, serialize


LOGGER = logging.getLogger(__name__)


class BaseEvent:

    @property
    def NAME(self):
        raise NotImplementedError

    @property
    def EVENTS(self):
        raise NotImplementedError

    def parse_evt(self, evt):
        raise NotImplementedError

    def prepare_response(self, state, validated_data):
        raise NotImplementedError

    def validate(self, msg_id, params):
        raise NotImplementedError

    async def produce_custom_msg(self, stream, validated_data):
        pass

    @classmethod
    def prepare_subscribe_message(cls, event_types, from_block=None):
        last_known_block_ids = [from_block] if from_block else []
        LOGGER.debug(f'last_known_block_ids {last_known_block_ids}')
        return cls.create_subscribe_request(event_types, last_known_block_ids)

    @classmethod
    def prepare_events(cls, event_types):
        for event_type in event_types:
            instance = EVENT_TRANSLATOR.get(event_type)
            if not instance:
                continue
            yield from instance.EVENTS

    @classmethod
    def create_subscriptions(cls, event_types):
        return [EventSubscription(event_type=event_name)
                for event_name in cls.prepare_events(event_types)]

    @classmethod
    def create_subscribe_request(cls, event_types, last_known_block_ids):
        return ClientEventsSubscribeRequest(subscriptions=cls.create_subscriptions(event_types),
                                            last_known_block_ids=last_known_block_ids)


class BlockEvent(BaseEvent):

    NAME = 'blocks'
    EVENTS = (
        Events.SAWTOOTH_BLOCK_COMMIT.value,
    )

    def prepare_response(self, state, validated_data):
        return {'id': state}

    def parse_evt(self, evt):
        try:
            return next(filter(lambda el: el['key'] == 'block_id', evt['attributes']))['value']
        except StopIteration:
            pass

    def validate(self, msg_id, params):
        return {}


class BatchEvent(BaseEvent):

    NAME = 'batch'
    EVENTS = (
        Events.REMME_BATCH_DELTA.value,
    )

    def prepare_response(self, state, validated_data):
        return state

    def parse_evt(self, evt):
        return {evt['key']: evt['value'] for evt in evt['attributes']}

    def validate(self, msg_id, params):
        try:
            id = params['id']
        except KeyError:
            raise RpcInvalidParamsError(message='Missed id', msg_id=msg_id)

        return {
            'id': id
        }

    async def produce_custom_msg(self, stream, validated_data):
        batch_id = validated_data['id']
        router = Router(stream)
        try:
            result = await router.list_statuses([batch_id])
        except Exception as e:
            LOGGER.warning(f'Error during fetch: {e}')
            return

        status = result['data'][0]['status']

        evt_resp = EventList(
            events=[Event(
                event_type=Events.REMME_BATCH_DELTA.value,
                attributes=[
                    Event.Attribute(key='id', value=batch_id),
                    Event.Attribute(key='status', value=status),
                ]
            )]
        )
        correlation_id = uuid.uuid4().hex
        msg = Message(
            correlation_id=correlation_id,
            content=evt_resp.SerializeToString(),
            message_type=Message.CLIENT_EVENTS)
        await stream.route_msg(msg)


class TransferEvent(BaseEvent):

    NAME = 'transfer'
    EVENTS = (
        Events.ACCOUNT_TRANSFER.value,
    )

    def prepare_response(self, state, validated_data):
        sender, receiver = state[0], state[1]
        if any([
            sender['address'] == validated_data['address'],
            receiver['address'] != validated_data['address']
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
            return deserialize(next(filter(lambda el: el['key'] == 'entities_changed', evt['attributes']))['value'])
        except StopIteration:
            pass

    def validate(self, msg_id, params):
        try:
            address = params['address']
        except KeyError:
            raise RpcInvalidParamsError(message='Missed address', msg_id=msg_id)

        return {
            'address': address
        }


class AtomicSwapEvent(BaseEvent):

    NAME = 'atomic_swap'
    EVENTS = (
        Events.SWAP_INIT.value,
        Events.SWAP_CLOSE.value,
        Events.SWAP_APPROVE.value,
        Events.SWAP_EXPIRE.value,
        Events.SWAP_SET_SECRET_LOCK.value,
    )

    def prepare_response(self, state, validated_data):
        swap_info = next(filter(lambda el: el['type'] == 'AtomicSwapInfo', state))
        LOGGER.debug(f'Parsed swap info: {swap_info}')

        if validated_data['id'] == swap_info['swap_id']:
            del swap_info['type']
            return swap_info

    def parse_evt(self, evt):
        try:
            return deserialize(next(filter(lambda el: el['key'] == 'entities_changed', evt['attributes']))['value'])
        except StopIteration:
            pass

    def validate(self, msg_id, params):
        try:
            id = params['id']
        except KeyError:
            raise RpcInvalidParamsError(message='Missed id', msg_id=msg_id)

        from_block = params.get('from_block')
        if from_block and not isinstance(from_block, str):
            raise ClientException(message='Invalid "from_block" type',
                                  msg_id=id)
        return {
            'from_block': from_block,
            'id': id
        }


EVENT_TRANSLATOR = {
    BlockEvent.NAME: BlockEvent(),
    BatchEvent.NAME: BatchEvent(),
    TransferEvent.NAME: TransferEvent(),
    AtomicSwapEvent.NAME: AtomicSwapEvent(),
}
SAWTOOTH_TO_REMME_EVENT = {evt_type: evt.NAME for evt in EVENT_TRANSLATOR.values() for evt_type in evt.EVENTS}


class EventWebSocketHandler:

    def __init__(self, zmq_url, *, loop=None):
        self._zmq_url = zmq_url
        self._accepting = True
        self._sockets = {}
        self._evthashes = {}
        self._subsevt = {}
        self._loop = loop or asyncio.get_event_loop()

        self._consumer_task = weakref.ref(
            asyncio.ensure_future(self.consumer(), loop=self._loop))
        self._producer_task = weakref.ref(
            asyncio.ensure_future(self.producer(), loop=self._loop))
        self._print_storage_state_task = weakref.ref(
            asyncio.ensure_future(self.print_storage_state(), loop=self._loop))

        self._consumer_running = True
        self._producer_running = True
        self._print_storage_state_running = True

    async def on_shutdown(self):
        self._consumer_running = False
        self._producer_running = False
        self._print_storage_state_running = False

        for ws in self._sockets:
            await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    async def __call__(self, request):
        if not self._accepting:
            return web.Response(status=503)

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        LOGGER.debug('WS ready')

        stream = Connection(self._zmq_url, loop=self._loop)
        await stream.open()

        LOGGER.debug('ZMQ ready')

        with self.register(ws, stream):
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        await self.handle_message(ws, msg.data)
                    except RpcError as e:
                        await self.send_error(ws, e.error_code, e.message,
                                              e.msg_id)
                    except Exception as e:
                        LOGGER.exception(e)
                        await self.send_error(ws, -32603, 'Internal error')

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    LOGGER.warning(
                        'Web socket connection closed with exception %s',
                        ws.exception())
                    await ws.close()

        return ws

    @contextmanager
    def register(self, ws, stream):
        try:
            self._sockets[ws] = stream
            yield
        finally:
            stream.close()
            with suppress(KeyError):
                del self._sockets[ws]
            with suppress(KeyError):
                del self._subsevt[ws]
            with suppress(KeyError):
                del self._evthashes[ws]

    async def send_msg(self, ws, result, id):
        prepared = serialize({"jsonrpc": "2.0", "id": id, "result": result})
        await ws.send_str(prepared)

    async def send_error(self, ws, err_msg, code, id=None):
        error = {
            'code': code,
            'message': err_msg,
        }
        prepared = serialize({"jsonrpc": "2.0", "id": id, "error": error})
        await ws.send_str(prepared)

    async def handle_message(self, ws, message_content):
        try:
            data = deserialize(message_content)
        except Exception:
            raise ClientException(message='Could not deserialize')

        jsonrpc = data.get('jsonrpc', '2.0')
        params = data.get('params', {})
        id = data.get('id', None)

        try:
            method = data['method']
        except KeyError:
            err_msg = 'Method not found'
            raise RpcMethodNotFoundError(msg_id=id, message=err_msg)

        try:
            event_type = params['event_type']
        except KeyError as e:
            raise ClientException(message='Missed event_type', msg_id=id)

        if method == 'subscribe':
            await self.subscribe(ws, id, event_type, params)
        elif method == 'unsubscribe':
            await self.unsubscribe(ws, id, event_type)
        else:
            raise ClientException(message='Method not found', msg_id=id)

    async def subscribe(self, ws, id, event_type, params):
        try:
            evt_tr = EVENT_TRANSLATOR[event_type]
        except KeyError:
            raise ClientException(
                message=f'Event "{event_type}" not defined',
                msg_id=id)

        subsevt = self._subsevt.setdefault(ws, {})
        if event_type in subsevt:
            raise ClientException(
                message=f'Already subscribed to event "{event_type}"',
                msg_id=id)

        stream = self._sockets[ws]
        router = Router(stream)

        event_types = set(subsevt.keys())
        event_types.add(event_type)

        validated_data = evt_tr.validate(id, params)
        from_block = validated_data.get('from_block')
        if not from_block:
            from_block = (await router.list_blocks(limit=1))['head']

        req_msg = evt_tr.prepare_subscribe_message(event_types, from_block)

        LOGGER.debug(f'Request message: {req_msg}')

        msg = await stream.send(
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            message_content=req_msg.SerializeToString(),
            timeout=ZMQ_CONNECTION_TIMEOUT)

        LOGGER.debug(f'Message type: {msg.message_type}')

        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            raise ClientException(
                message=f'Unexpected message type {msg.message_type}',
                msg_id=id)

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            if response.status == ClientEventsSubscribeResponse.UNKNOWN_BLOCK:
                raise ClientException(
                    message=f'Unknown block "{from_block}"', msg_id=id)
            raise ClientException(
                message='Subscription failed: Couldn\'t '
                        'send multipart', msg_id=id)

        if ws not in self._evthashes:
            self._evthashes[ws] = set()

        subsevt[event_type] = {
            'msg_id': id,
            'validated_data': validated_data,
        }

        await self.send_msg(ws, 'SUBSCRIBED', id)

    async def unsubscribe(self, ws, id, event_type):
        subsevt = self._subsevt.get(ws, {})
        try:
            del subsevt[event_type]
        except KeyError:
            raise ClientException(
                message='Subscription not found', msg_id=id)

        await self.send_msg(ws, 'UNSUBSCRIBED', id)

    async def consumer(self):
        while self._consumer_running:
            LOGGER.debug('Consumer: Start fetching a new messages...')
            datas = []
            for ws, stream in self._sockets.items():
                try:
                    msg = stream.receive_nowait()
                except asyncio.QueueEmpty:
                    continue
                else:
                    LOGGER.debug('Msg received for zmq socket '
                                f'{stream._socket}')
                    datas.append((ws, stream, msg))

            await asyncio.gather(*(self._process_msg(*data) for data in datas))
            LOGGER.debug('Consumer: Waiting...')
            await asyncio.sleep(1, loop=self._loop)

    async def producer(self):
        while self._producer_running:
            LOGGER.debug('Producer: Start producing a new messages...')
            for ws, stream in self._sockets.items():
                for evt_name, data in self._subsevt.get(ws, {}).items():
                    evt_tr = EVENT_TRANSLATOR[evt_name]
                    await evt_tr.produce_custom_msg(stream, data['validated_data'])
            LOGGER.debug('Producer: Waiting...')
            await asyncio.sleep(1, loop=self._loop)

    async def print_storage_state(self):
        while self._print_storage_state_running:
            await asyncio.sleep(5)
            LOGGER.debug(f'Event hashes: {self._evthashes}')
            LOGGER.debug(f'ws2zmq connections: {self._sockets}')
            LOGGER.debug(f'Events subscriptions: {self._subsevt}')

    async def _process_msg(self, ws, stream, msg):
        LOGGER.debug(f'Message type: {msg.message_type}')

        if msg.message_type != Message.CLIENT_EVENTS:
            LOGGER.debug(f'Skip unexpected msg type {msg.message_type}')
            return

        evt_resp = EventList()
        evt_resp.ParseFromString(msg.content)

        evthash = hashlib.sha256(evt_resp.SerializeToString()).hexdigest()
        LOGGER.debug(f'Evt hash calculated: {evthash}')
        data = message_to_dict(evt_resp)
        LOGGER.debug(f'Dicted response data: {data}')

        subsevt = self._subsevt.get(ws, {})

        for evt in data['events']:
            event_type = evt['event_type']

            evt_name = SAWTOOTH_TO_REMME_EVENT.get(event_type)
            if not evt_name:
                LOGGER.debug(f'Evt name for type "{event_type}" '
                             'not configured')
                continue

            evt_tr = EVENT_TRANSLATOR[evt_name]

            # Check if evt_name is subscribed
            if evt_name not in subsevt:
                LOGGER.debug('No active ws connection '
                             f'for evt "{evt_name}"')
                continue

            # Check if ws has stored hashes
            if ws not in self._evthashes:
                LOGGER.warning(f'Connection {ws.socket_id} not found')
                del subsevt[evt_name]
                continue

            # Check if we already have sent update
            if evthash in self._evthashes[ws]:
                LOGGER.debug(f'Connection {ws} already '
                             'received this notification')
                continue

            # get response of updated state
            LOGGER.debug(f'Got evt data: {evt}')
            updated_state = evt_tr.parse_evt(evt)
            if not updated_state:
                LOGGER.debug('Skiping evt with no state update')
                continue

            validated_data = subsevt[evt_name]['validated_data']
            LOGGER.debug(f'Loaded validated data: {validated_data}')
            msg_id = subsevt[evt_name]['msg_id']
            response = evt_tr.prepare_response(updated_state, validated_data)
            if not response:
                LOGGER.debug('Skiping evt with empty response')
                continue

            data = {
                'event_type': evt_name,
                'attributes': response
            }

            await self.send_msg(ws, data, msg_id)
            self._evthashes[ws].add(evthash)
