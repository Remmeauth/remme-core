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

import argparse
import asyncio
import toml
from aiohttp import web
from zmq.asyncio import ZMQEventLoop
from sawtooth_sdk.messaging.stream import Stream
from remme.shared.logging import setup_logging
from .ws import WsApplicationHandler

if __name__ == '__main__':
    config = toml.load('/config/remme-client-config.toml')['remme']['client']
    zmq_url = f'tcp://{ config["validator_ip"] }:{ config["validator_port"] }'
    setup_logging('remme.ws')
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='0.0.0.0')
    arguments = parser.parse_args()
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
    app = web.Application(loop=loop)
    stream = Stream(zmq_url)
    ws_handler = WsApplicationHandler(stream, loop=loop)
    app.router.add_route('GET', '/ws', ws_handler.subscriptions)
    web.run_app(app, host=arguments.bind, port=arguments.port)
