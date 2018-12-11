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
import asyncio

from aiohttp_json_rpc.protocol import encode_result
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf.client_event_pb2 import (
    ClientEventsSubscribeResponse,
)
from sawtooth_sdk.protobuf.events_pb2 import EventList

from remme.settings import ZMQ_CONNECTION_TIMEOUT
from remme.shared.utils import message_to_dict
from remme.shared.exceptions import ClientException

from ._handlers import EVENT_HANDLERS, SAWTOOTH_TO_REMME_EVENT


LOGGER = logging.getLogger(__name__)
event_lock = asyncio.Lock()


async def subscribe(request):
    ws = request.ws
    if ws is None:
        raise ClientException(
            message='Subscription available only through websocket')

    msg_id = request.msg.data['id']

    request.params = request.params or {}
    try:
        event_type = request.params['event_type']
    except KeyError as e:
        raise RpcInvalidParamsError(message='Missed event_type')

    try:
        evt_tr = EVENT_HANDLERS[event_type]
    except KeyError:
        raise ClientException(
            message=f'Event "{event_type}" not defined')

    async with event_lock:
        subsevt = request.rpc._subsevt.setdefault(ws, {})
        if event_type in subsevt:
            raise ClientException(
                message=f'Already subscribed to event "{event_type}"')

        router = ws.stream.router

        event_types = set(subsevt.keys())
        event_types.add(event_type)

        LOGGER.debug(f'Events to re-subsribe: {event_types}')

        validated_data = evt_tr.validate(msg_id, request.params)
        from_block = validated_data.get('from_block')
        if not from_block:
            from_block = (await router.list_blocks(limit=1))['head']

        req_msg = evt_tr.prepare_subscribe_message(event_types, from_block)

        LOGGER.debug(f'Request message: {req_msg}')

        msg = await ws.stream.send(
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            message_content=req_msg.SerializeToString(),
            timeout=ZMQ_CONNECTION_TIMEOUT)

        LOGGER.debug(f'Message type: {msg.message_type}')

        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            raise ClientException(
                message=f'Unexpected message type {msg.message_type}')

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            if response.status == ClientEventsSubscribeResponse.UNKNOWN_BLOCK:
                raise ClientException(
                    message=f'Unknown block "{from_block}"')
            raise ClientException(
                message='Subscription failed: Couldn\'t '
                        'send multipart')

        if ws not in request.rpc._evthashes:
            request.rpc._evthashes[ws] = set()

        LOGGER.debug(f'Create cosumer task for {ws}')
        request.rpc.loop.create_task(_consumer(request))

        if event_type == 'batch':
            LOGGER.debug(f'Create producer task for {ws}')
            request.rpc.loop.create_task(_producer(request))

        subsevt[event_type] = {
            'msg_id': msg_id,
            'validated_data': validated_data,
        }

    return 'SUBSCRIBED'


async def unsubscribe(request):
    ws = request.ws
    if ws is None:
        raise ClientException(
            message='Subscription available only through websocket')

    request.params = request.params or {}
    try:
        event_type = request.params['event_type']
    except KeyError as e:
        raise RpcInvalidParamsError(message='Missed event_type')

    async with event_lock:
        subsevt = request.rpc._subsevt.get(ws, {})
        try:
            del subsevt[event_type]
        except KeyError:
            raise ClientException(
                message='Subscription not found')

    return 'UNSUBSCRIBED'


async def _producer(request):
    ws = request.ws
    stream = ws.stream

    while not ws.closed:
        LOGGER.debug('Producer: Start producing a new messages...')
        for evt_name, data in request.rpc._subsevt.get(ws, {}).items():
            evt_tr = EVENT_HANDLERS[evt_name]
            await evt_tr.produce_custom_msg(stream, data['validated_data'])
        LOGGER.debug('Producer: Waiting...')
        await asyncio.sleep(1)


async def _consumer(request):
    ws = request.ws
    stream = ws.stream

    while not ws.closed:
        LOGGER.debug(f'Consumer: Start fetching a new messages for {ws}...')
        try:
            msg = await stream.receive()
        except asyncio.QueueEmpty:
            continue
        LOGGER.debug(f'Msg received from socket {msg}')
        await _process_msg(request, msg)
        LOGGER.debug(f'Consumer: Waiting new messages for {ws}...')


async def _process_msg(request, msg):
    LOGGER.debug(f'Message type: {msg.message_type}')

    if msg.message_type != Message.CLIENT_EVENTS:
        LOGGER.debug(f'Skip unexpected msg type {msg.message_type}')
        return

    evt_resp = EventList()
    evt_resp.ParseFromString(msg.content)

    ws = request.ws
    subsevt = request.rpc._subsevt.get(ws, {})

    for proto_data in evt_resp.events:
        evt = message_to_dict(proto_data)
        LOGGER.debug(f'Dicted response evt: {evt}')

        event_type = evt['event_type']

        evt_names = SAWTOOTH_TO_REMME_EVENT.get(event_type)
        if not evt_names:
            LOGGER.debug(f'Evt names for type "{event_type}" '
                         'not configured')
            continue

        for evt_name in evt_names:
            evt_tr = EVENT_HANDLERS[evt_name]

            # Check if evt_name is subscribed
            if evt_name not in subsevt:
                LOGGER.debug('No active ws connection '
                             f'for evt "{evt_name}"')
                continue

            # Check if ws has stored hashes
            if ws not in request.rpc._evthashes:
                LOGGER.warning(f'Connection {ws} not found')
                del subsevt[evt_name]
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
            if asyncio.iscoroutine(response):
                response = await response

            if not response:
                LOGGER.debug('Skiping evt with empty response')
                continue

            LOGGER.debug(f'Got response: {response}')
            evthash = evt_tr.prepare_evt_hash(response)
            LOGGER.debug(f'Evt hash calculated: {evthash}')

            # Check if we already have sent update
            if evthash in request.rpc._evthashes[ws]:
                LOGGER.debug(f'Connection {ws} already '
                             'received this notification')
                continue

            result = encode_result(msg_id, {
                'event_type': evt_name,
                'attributes': response
            })
            await request.rpc._ws_send_str(request, result)

            request.rpc._evthashes[ws].add(evthash)
