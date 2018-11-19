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

# pylint: disable=invalid-name

import argparse
import asyncio
import logging

from aiohttp import web
import aiohttp_cors

from zmq.asyncio import ZMQEventLoop
from remme.shared.logging_setup import setup_logging

from remme.shared.stream import Stream
from remme.ws import WsApplicationHandler, WsEventSocketHandler
from remme.settings.default import load_toml_with_defaults

from .base import JsonRpc


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    cfg_rpc = load_toml_with_defaults(
        '/config/remme-rpc-api.toml'
    )['remme']['rpc_api']

    cfg_ws = load_toml_with_defaults(
        '/config/remme-client-config.toml'
    )['remme']['client']

    setup_logging('remme-rpc-api')
    parser = argparse.ArgumentParser()

    parser.add_argument('--port', type=int, default=cfg_rpc["port"])
    parser.add_argument('--bind', default=cfg_rpc["bind"])
    arguments = parser.parse_args()

    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    app = web.Application(loop=loop)
    cors_config = cfg_rpc["cors"]
    # enable CORS
    if isinstance(cors_config["allow_origin"], str):
        cors_config["allow_origin"] = [cors_config["allow_origin"]]

    cors = aiohttp_cors.setup(app, defaults={
        ao: aiohttp_cors.ResourceOptions(
            allow_methods=cors_config["allow_methods"],
            max_age=cors_config["max_age"],
            allow_credentials=cors_config["allow_credentials"],
            allow_headers=cors_config["allow_headers"],
            expose_headers=cors_config["expose_headers"]
        ) for ao in cors_config["allow_origin"]
    })
    rpc = JsonRpc(loop=loop, max_workers=1)
    rpc.load_from_modules(cfg_rpc['available_modules'])
    cors.add(app.router.add_route('GET', '/', rpc))
    cors.add(app.router.add_route('POST', '/', rpc))

    # Remme ws
    stream = Stream(f'tcp://{ cfg_ws["validator_ip"] }:{ cfg_ws["validator_port"] }')
    ws_handler = WsApplicationHandler(stream, loop=loop)
    cors.add(app.router.add_route('GET', '/ws', ws_handler.subscriptions))
    ws_event_handler = WsEventSocketHandler(stream, loop=loop)
    # FIXME: Merge with one ws in future
    cors.add(app.router.add_route('GET', '/ws/events', ws_event_handler.subscriptions))

    logger.info('All server parts loaded')

    web.run_app(app, host=arguments.bind, port=arguments.port)
