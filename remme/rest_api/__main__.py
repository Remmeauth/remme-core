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
import argparse
from pkg_resources import resource_filename

import connexion
from aiohttp import web
from zmq.asyncio import ZMQEventLoop


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='0.0.0.0')
    parser.add_argument('--zmq_url', default='tcp://validator:4004')
    parser.add_argument('--server_type', default='rest_api')
    arguments = parser.parse_args()

    if arguments.server_type == 'rest_api':
        from .api_methods_switcher import RestMethodsSwitcherResolver  # noqa

        app = connexion.FlaskApp(__name__, specification_dir='.')
        app.add_api(resource_filename(__name__, 'openapi.yml'), resolver=RestMethodsSwitcherResolver('remme.rest_api'))
        app.run(port=arguments.port, host=arguments.bind)
    elif arguments.server_type == 'ws':
        # NOTE: Here because of breaking up protos
        from sawtooth_rest_api.messaging import Connection

        from .ws import WsApplicationHandler  # noqa

        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        app = web.Application(loop=loop)
        connection = Connection(arguments.zmq_url)
        loop.run_until_complete(connection._do_start())
        ws_handler = WsApplicationHandler(connection, loop=loop)
        app.router.add_route('GET', '/ws', ws_handler.subscriptions)
        web.run_app(app, host=arguments.bind, port=arguments.port)
    else:
        raise RuntimeError('Do not support "%s" type' % arguments.server_type)
