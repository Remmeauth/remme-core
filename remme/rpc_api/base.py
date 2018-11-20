import logging

import aiohttp
from aiohttp import web
from aiohttp_json_rpc import JsonRpc
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

from remme.shared.exceptions import RemmeRpcError
from .utils import load_methods


LOGGER = logging.getLogger(__name__)


class JsonRpc(JsonRpc):

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
            return (await self.handle_http_request(request))

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

    async def handle_http_request(self, http_request):
        raw_msg = await http_request.read()
        try:
            msg = decode_msg(raw_msg)
            self.logger.debug('message decoded: %s', msg)

        except RpcError as error:
            return self._http_send_str(http_request, encode_error(error))

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

                return self._http_send_str(http_request, encode_error(
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

                return self._http_send_str(http_request, result)

            except (RpcGenericServerDefinedError,
                    RpcInvalidRequestError,
                    RpcInvalidParamsError,
                    RemmeRpcError) as error:

                return self._http_send_str(
                    http_request,
                    encode_error(error, id=msg.data.get('id', None))
                )

            except Exception as error:
                logging.error(error, exc_info=True)

                return self._http_send_str(http_request, encode_error(
                    RpcInternalError(msg_id=msg.data.get('id', None))
                ))

        # handle result
        elif msg.type == JsonRpcMsgTyp.RESULT:
            self.logger.debug('msg gets handled as result')

            result = encode_result(msg.data['id'], msg.data['result'])
            return self._http_send_str(http_request, result)
        else:
            self.logger.debug('unsupported msg type (%s)', msg.type)

            return self._http_send_str(http_request, encode_error(
                RpcInvalidRequestError(msg_id=msg.data.get('id', None))
            ))

    def _http_send_str(self, request, string):
        return web.json_response(string, dumps=lambda obj, *a, **kw: obj)
