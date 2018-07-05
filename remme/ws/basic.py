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
import hashlib
import weakref
import re

import aiohttp
from aiohttp import web

from .constants import Action, Entity, Status, Type
from .utils import deserialize, serialize

LOGGER = logging.getLogger(__name__)


class BasicWebSocketHandler(object):

    def __init__(self, stream, loop):
        self._stream = stream
        # mapping websocket => something valuable
        self._subscribers = {}
        self._subscriber_lock = asyncio.Lock()
        self._accepting = True

        self._loop = loop

    async def on_shutdown(self):
        await self._unregister_subscriptions()

        self._accepting = False

        for ws, _ in self._subscribers.items():
            await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    async def subscriptions(self, request):
        if not self._accepting:
            return web.Response(status=503)

        web_sock = web.WebSocketResponse()
        await web_sock.prepare(request)

        async for msg in web_sock:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._handle_message(web_sock, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                LOGGER.warning(
                    'Web socket connection closed with exception %s',
                    web_sock.exception())
                await web_sock.close()

        await self._handle_unsubscribe(web_sock)

        return web_sock

    def get_response_payload(self, type, data):
        return {
            'type': type,
            'data': data
        }

    async def _ws_send_message(self, ws, data):
        await self._ws_send(ws, self.get_response_payload(Type.MESSAGE, data))

    async def _ws_send_error(self, ws, error):
        await self._ws_send(ws, self.get_response_payload(Type.ERROR, error))

    async def _ws_send(self, ws, payload):
        return await ws.send_str(serialize(payload))

    async def _handle_message(self, web_sock, message_content):
        try:
            LOGGER.info(f'Incoming message {message_content}')
            payload = deserialize(message_content)
        except Exception:
            await self._ws_send_error(web_sock, Status.MALFORMED_JSON)
            return

        LOGGER.info('Got payload: %s' % payload)

        err_code = self.validate_payload(payload)

        if err_code:
            await self._ws_send_error(web_sock, err_code)
            return

        try:
            action = Action(payload['action'])
        except ValueError:
            await self._ws_send(web_sock, Status.INVALID_ACTION)
            return

        LOGGER.info('Determined action: %s', action)

        data = payload['data']
        if action == Action.SUBSCRIBE:
            await self._handle_subscribe(web_sock, data)

        elif action == Action.UNSUBSCRIBE:
            await self._handle_unsubscribe(web_sock, data)

    def validate_payload(self, payload):
        action = payload.get('action')
        if not action:
            return Status.MISSING_ACTION
        data = payload.get('data')
        if not data:
            return Status.MISSING_DATA
        if action == Action.SUBSCRIBE:
            if not data.get('entity'):
                return Status.MISSING_ENTITY

    async def _handle_subscribe(self, web_sock, data):
        LOGGER.info('Sending initial most recent event to new subscriber')

        try:
            entity = Entity(data['entity'])
        except ValueError:
            await self._ws_send_error(web_sock, Status.INVALID_ENTITY)
            return

        with await self._subscriber_lock:
            self._subscribers[web_sock] = self.subscribe(entity, data)
            LOGGER.info('Subscribed: %s', web_sock)

        await self._ws_send_message(web_sock, Status.SUBSCRIBED)

    def subscribe(self, entity, data):
        pass

    def unsubscribe(self, entity, data):
        pass

    async def _handle_unsubscribe(self, web_sock, payload=None):
        with await self._subscriber_lock:
            if web_sock in self._subscribers:
                del self._subscribers[web_sock]

            if payload:
                data = payload.get('data', {})

                try:
                    entity = Entity(payload['entity'])
                except ValueError:
                    await self._ws_send(web_sock, Status.INVALID_ENTITY, payload['id'])
                    return

                self.unsubscribe(web_sock, entity, data)
            await self._ws_send(web_sock, Status.UNSUBSCRIBED, payload['id'])

            LOGGER.info('Unsubscribed: %s', web_sock)

    async def _handle_disconnect(self):
        LOGGER.info('Validator disconnected')
        for ws, _ in self._subscribers.items():
            await self._ws_send(ws, Status.NO_VALIDATOR)
