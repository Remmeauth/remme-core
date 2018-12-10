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
import weakref
import asyncio
import threading
from contextlib import contextmanager, suppress

import aiohttp
from aiohttp import web

from aiohttp_json_rpc.rpc import JsonRpc
from aiohttp_json_rpc.protocol import (
    JsonRpcMsgTyp,
    encode_result,
    encode_error,
    decode_msg,
)
from aiohttp_json_rpc.exceptions import (
    RpcGenericServerDefinedError,
    RpcInvalidRequestError,
    RpcMethodNotFoundError,
    RpcInvalidParamsError,
    RpcInternalError,
    RpcError,
)

from remme.shared.router import Router
from remme.shared.exceptions import RemmeRpcError
from remme.shared.messaging import Connection
from .utils import load_methods


LOGGER = logging.getLogger(__name__)


class JsonRpc(JsonRpc):

    def __init__(self, zmq_url, websocket_state_logger=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zmq_url = zmq_url
        self._accepting = True
        self._evthashes = {}
        self._subsevt = {}

        if websocket_state_logger:
            self._print_storage_state_task = weakref.ref(
                asyncio.ensure_future(self._print_storage_state(), loop=self.loop))
            self._print_storage_state_running = True

    async def __call__(self, request):
        # prepare request
        request.rpc = self
        self.auth_backend.prepare_request(request)

        # handle request
        if request.method == 'GET':

            # handle Websocket
            if request.headers.get('upgrade', '').lower() == 'websocket':
                return (await self.handle_websocket_request(request))
            # handle GET
            return aiohttp.web.Response(status=405)

        # handle POST
        elif request.method == 'POST':
            return (await self._handle_rpc_msg(request))

    def load_from_modules(self, modules):
        self.add_methods(
            *(('', method) for method in load_methods('remme.rpc_api',
                                                      modules)))

    @property
    def rpc_methods(self):
        if not hasattr(self, '_rpc_methods'):
            self._rpc_methods = {
                method.__name__ for method in load_methods('remme.rpc_api')
            }
        return self._rpc_methods

    @contextmanager
    def register(self, ws, stream):
        try:
            ws.stream = stream
            ws.stream.router = Router(stream)
            yield
        finally:
            stream.close()
            with suppress(KeyError):
                del ws.stream
            with suppress(KeyError):
                del self._subsevt[ws]
            with suppress(KeyError):
                del self._evthashes[ws]

    async def handle_websocket_request(self, http_request):
        if not self._accepting:
            return web.Response(status=503)

        http_request.pending = {}

        LOGGER.debug('WS ready')

        stream = Connection(self._zmq_url, loop=self.loop)
        await stream.open()

        LOGGER.debug('ZMQ ready')

        # prepare and register websocket
        ws = aiohttp.web_ws.WebSocketResponse()
        await ws.prepare(http_request)
        LOGGER.debug('WS ready')

        http_request.ws = ws
        self.clients.append(http_request)

        with self.register(ws, stream):
            while not ws.closed:
                self.logger.debug('waiting for messages')
                raw_msg = await ws.receive()

                if not raw_msg.type == aiohttp.WSMsgType.TEXT:
                    continue

                self.logger.debug('raw msg received: %s', raw_msg.data)
                self.loop.create_task(
                    self._handle_rpc_msg(http_request, raw_msg))

        self.clients.remove(http_request)

        return ws

    async def _handle_rpc_msg(self, http_request, data=None):
        if not data:
            raw_msg = await http_request.read()
        else:
            raw_msg = data.data
        try:
            msg = decode_msg(raw_msg)
            self.logger.debug('message decoded: %s', msg)

        except RpcError as error:
            return await self._send_str(http_request, encode_error(error))

        # handle requests
        if msg.type == JsonRpcMsgTyp.REQUEST:
            self.logger.debug('msg gets handled as request')

            # check if method is available
            if msg.data['method'] not in http_request.methods:
                self.logger.debug('method %s is unknown or restricted',
                                  msg.data['method'])
                if msg.data['method'] in self.rpc_methods:
                    err_msg = 'Method is disabled by the node administrator'
                else:
                    err_msg = 'Method not found'

                return await self._send_str(http_request, encode_error(
                    RpcMethodNotFoundError(msg_id=msg.data.get('id', None),
                                           message=err_msg)
                ))

            # call method
            raw_response = getattr(
                http_request.methods[msg.data['method']].method,
                'raw_response',
                False,
            )

            try:
                result = await http_request.methods[msg.data['method']](
                    http_request=http_request,
                    rpc=self,
                    msg=msg,
                )

                if not raw_response:
                    result = encode_result(msg.data['id'], result)

                return await self._send_str(http_request, result)

            except (RpcGenericServerDefinedError,
                    RpcInvalidRequestError,
                    RpcInvalidParamsError,
                    RemmeRpcError) as error:

                return await self._send_str(
                    http_request,
                    encode_error(error, id=msg.data.get('id', None))
                )

            except Exception as error:
                logging.error(error, exc_info=True)

                return await self._send_str(http_request, encode_error(
                    RpcInternalError(msg_id=msg.data.get('id', None))
                ))

        # handle result
        elif msg.type == JsonRpcMsgTyp.RESULT:
            self.logger.debug('msg gets handled as result')

            result = encode_result(msg.data['id'], msg.data['result'])
            return await self._send_str(http_request, result)
        else:
            self.logger.debug('unsupported msg type (%s)', msg.type)

            return await self._send_str(http_request, encode_error(
                RpcInvalidRequestError(msg_id=msg.data.get('id', None))
            ))

    def _http_send_str(self, request, string):
        return web.json_response(string, dumps=lambda obj, *a, **kw: obj)

    async def _send_str(self, request, string):
        if request.protocol._upgrade:
            return await self._ws_send_str(request, string)
        return self._http_send_str(request, string)

    async def _print_storage_state(self):
        while self._print_storage_state_running:
            await asyncio.sleep(5)
            LOGGER.debug(f'Event hashes: {self._evthashes}')
            LOGGER.debug(f'Event subscriptions: {self._subsevt}')
            LOGGER.debug(f'Active threads count: {threading.active_count()}')
