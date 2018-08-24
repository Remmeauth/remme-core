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
import logging

import toml
from pkg_resources import resource_filename
import connexion
import aiohttp_cors

from zmq.asyncio import ZMQEventLoop
from sawtooth_sdk.messaging.stream import Stream
from remme.rest_api.api_methods_switcher import RestMethodsSwitcherResolver
from remme.rest_api.api_handler import AioHttpApi
from remme.rest_api.validator import proxy
from remme.shared.logging import setup_logging
from remme.ws import WsApplicationHandler
from remme.settings.default import load_toml_with_defaults


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    cfg_rest = load_toml_with_defaults('/config/remme-rest-api.toml')['remme']['rest_api']
    cfg_ws = load_toml_with_defaults('/config/remme-client-config.toml')['remme']['client']
    zmq_url = f'tcp://{ cfg_ws["validator_ip"] }:{ cfg_ws["validator_port"] }'

    setup_logging('rest-api')

    parser = argparse.ArgumentParser()

    parser.add_argument('--port', type=int, default=cfg_rest["port"])
    parser.add_argument('--bind', default=cfg_rest["bind"])
    arguments = parser.parse_args()

    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    app = connexion.AioHttpApp(__name__, specification_dir='.',
                               swagger_ui=cfg_rest['swagger']['enable_ui'],
                               swagger_json=cfg_rest['swagger']['enable_json'])
    cors_config = cfg_rest["cors"]
    # enable CORS
    if isinstance(cors_config["allow_origin"], str):
        cors_config["allow_origin"] = [cors_config["allow_origin"]]

    cors = aiohttp_cors.setup(app.app, defaults={
        ao: aiohttp_cors.ResourceOptions(
            allow_methods=cors_config["allow_methods"],
            max_age=cors_config["max_age"],
            allow_credentials=cors_config["allow_credentials"],
            allow_headers=cors_config["allow_headers"],
            expose_headers=cors_config["expose_headers"]
        ) for ao in cors_config["allow_origin"]
    })
    # patch with update API cls
    app.api_cls = AioHttpApi
    # cors patch
    app.api_cls.cors = cors
    # Proxy to sawtooth rest api
    cors.add(app.app.router.add_route('GET', '/validator/{path:.*?}',
                                      proxy))
    # Remme ws
    stream = Stream(zmq_url)
    ws_handler = WsApplicationHandler(stream, loop=loop)
    cors.add(app.app.router.add_route('GET', '/ws', ws_handler.subscriptions))
    # Remme rest api spec
    app.add_api(resource_filename(__name__, 'openapi.yml'),
                resolver=RestMethodsSwitcherResolver('remme.rest_api',
                                                     cfg_rest["available_methods"]))

    app.run(port=arguments.port, host=arguments.bind)
