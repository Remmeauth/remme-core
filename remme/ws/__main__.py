import argparse
import asyncio
from aiohttp import web
from zmq.asyncio import ZMQEventLoop
from sawtooth_rest_api.messaging import Connection
from remme.shared.logging import setup_logging
from .ws import WsApplicationHandler

if __name__ == '__main__':
    setup_logging('remme.ws')
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--bind', default='0.0.0.0')
    parser.add_argument('--zmq_url', default='tcp://validator:4004')
    arguments = parser.parse_args()
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
    app = web.Application(loop=loop)
    connection = Connection(arguments.zmq_url)
    loop.run_until_complete(connection._do_start())
    ws_handler = WsApplicationHandler(connection, loop=loop)
    app.router.add_route('GET', '/ws', ws_handler.subscriptions)
    web.run_app(app, host=arguments.bind, port=arguments.port)
