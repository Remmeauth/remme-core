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
import asyncio
import logging

import zmq
import aiozmq
from aiozmq.stream import ZmqStream

from google.protobuf.message import DecodeError
from sawtooth_sdk.protobuf.validator_pb2 import Message


LOGGER = logging.getLogger(__name__)


class DisconnectError(Exception):
    """Raised when a connection disconnects.
    """

    def __init__(self):
        super().__init__("The connection was lost")


class SendBackoffTimeoutError(Exception):
    """Raised when the send times out.
    """

    def __init__(self):
        super().__init__("Timed out sending message over ZMQ")


class _Backoff:
    """Implements a simple backoff mechanism.
    """

    def __init__(self, max_retries=3, interval=100, error=Exception()):
        self.num_retries = 0
        self.max_retries = max_retries
        self.interval = interval
        self.error = error

    async def do_backoff(self, err_msg=" "):
        if self.num_retries == self.max_retries:
            LOGGER.warning("Failed sending message to the Validator. No more "
                           "retries left. Backoff terminated: %s",
                           err_msg)
            raise self.error

        self.num_retries += 1
        LOGGER.warning("Sleeping for %s ms after failed attempt %s of %s to "
                       "send message to the Validator: %s",
                       str(self.num_retries),
                       str(self.max_retries),
                       str(self.interval / 1000),
                       err_msg)

        await asyncio.sleep(self.interval / 1000)
        self.interval *= 2


class _Sender:
    """Manages Sending messages over a ZMQ socket.
    """

    def __init__(self, socket, msg_router):
        self._msg_router = msg_router
        self._socket = socket

    async def send(self, message_type, message_content, timeout=None):
        correlation_id = uuid.uuid4().hex

        self._msg_router.expect_reply(correlation_id)

        message = Message(
            correlation_id=correlation_id,
            content=message_content,
            message_type=message_type)

        # Send the message. Backoff and retry in case of an error
        # We want a short backoff and retry attempt, so use the defaults
        # of 3 retries with 200ms of backoff
        backoff = _Backoff(max_retries=3,
                           interval=200,
                           error=SendBackoffTimeoutError())

        while True:
            try:
                self._socket.write([message.SerializeToString()])
                break
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except zmq.error.Again as e:
                await backoff.do_backoff(err_msg=repr(e))

        return await self._msg_router.await_reply(correlation_id,
                                                  timeout=timeout)


class _Receiver:
    """Receives messages and forwards them to a _MessageRouter.
    """

    def __init__(self, socket, msg_router):
        self._socket = socket
        self._msg_router = msg_router

        self._is_running = False

    async def start(self):
        """Starts receiving messages on the underlying socket and passes them
        to the message router.
        """
        self._is_running = True

        while self._is_running:
            try:
                zmq_msg = await self._socket.read()

                message = Message()
                message.ParseFromString(zmq_msg[-1])

                await self._msg_router.route_msg(message)
            except DecodeError as e:
                LOGGER.warning('Unable to decode: %s', e)
            except zmq.ZMQError as e:
                LOGGER.warning('Unable to receive: %s', e)
                return
            except asyncio.CancelledError:
                self._is_running = False

    def cancel(self):
        self._is_running = False


class _MessageRouter:
    """Manages message, routing them either to an incoming queue or to the
    futures for expected replies.
    """

    def __init__(self):
        self._queue = asyncio.Queue()
        self._futures = {}

    async def _push_incoming(self, msg):
        return await self._queue.put(msg)

    async def incoming(self):
        """Returns the next incoming message.
        """
        msg = await self._queue.get()
        self._queue.task_done()
        return msg

    def incoming_nowait(self):
        """Returns the next incoming message or error.
        """
        msg = self._queue.get_nowait()
        self._queue.task_done()
        return msg

    def expect_reply(self, correlation_id):
        """Informs the router that a reply to the given correlation_id is
        expected.
        """
        self._futures[correlation_id] = asyncio.Future()

    def expected_replies(self):
        """Returns the correlation ids for the expected replies.
        """
        return (c_id for c_id in self._futures)

    async def await_reply(self, correlation_id, timeout=None):
        """Wait for a reply to a given correlation id.  If a timeout is
        provided, it will raise a asyncio.TimeoutError.
        """
        try:
            result = await asyncio.wait_for(
                self._futures[correlation_id], timeout=timeout)

            return result
        finally:
            del self._futures[correlation_id]

    def _set_reply(self, correlation_id, msg):
        if correlation_id in self._futures:
            try:
                self._futures[correlation_id].set_result(msg)
            except asyncio.InvalidStateError as e:
                LOGGER.error(
                    'Attempting to set result on already-resolved future: %s',
                    str(e))

    def _fail_reply(self, correlation_id, err):
        if correlation_id in self._futures and \
                not self._futures[correlation_id].done():
            try:
                self._futures[correlation_id].set_exception(err)
            except asyncio.InvalidStateError as e:
                LOGGER.error(
                    'Attempting to set exception on already-resolved future: '
                    '%s',
                    str(e))

    def fail_all(self, err):
        """Fail all the expected replies with a given error.
        """
        for c_id in self._futures:
            self._fail_reply(c_id, err)

    async def route_msg(self, msg):
        """Given a message, route it either to the incoming queue, or to the
        future associated with its correlation_id.
        """
        if msg.correlation_id in self._futures:
            LOGGER.debug('Correlation found, processing message')
            self._set_reply(msg.correlation_id, msg)
        else:
            LOGGER.debug('Correlation not found, send message to queue')
            await self._push_incoming(msg)


class Connection:
    """A connection, over which validator Message objects may be sent.
    """
    _instance = None

    def __init__(self, url, *, loop=None):
        self._url = url
        self._loop = loop or asyncio.get_event_loop()
        self._socket = ZmqStream(loop=loop, high=None, low=None,
                                 events_backlog=100)
        self._msg_router = _MessageRouter()
        self._receiver = _Receiver(self._socket, self._msg_router)
        self._sender = _Sender(self._socket, self._msg_router)

        self._recv_task = None

    @classmethod
    def get_single_connection(cls, url, *, loop=None):
        if cls._instance is None:
            cls._instance = cls(url, loop=loop)
        return cls._instance

    @property
    def has_transport(self):
        return bool(self._socket._transport)

    async def open(self):
        """Opens the connection.
        An open connection will monitor for disconnects from the remote end.
        Messages are either received as replies to outgoing messages, or
        received from an incoming queue.
        """
        LOGGER.info('Connecting to %s', self._url)

        tr, _ = await aiozmq.create_zmq_connection(
            lambda: self._socket._protocol,
            zmq.DEALER,
            connect=self._url,
            loop=self._loop)
        tr.set_write_buffer_limits()

        self._recv_task = asyncio.ensure_future(self._receiver.start())

    async def send(self, message_type, message_content, timeout=None):
        """Sends a message and returns a future for the response.
        """
        return await self._sender.send(
            message_type, message_content, timeout=timeout)

    async def receive(self):
        """Returns a future for an incoming message.
        """
        return await self._msg_router.incoming()

    async def route_msg(self, msg):
        return await self._msg_router.route_msg(msg)

    def receive_nowait(self):
        return self._msg_router.incoming_nowait()

    def close(self):
        """Closes the connection.
         All outstanding futures for replies will be sent a DisconnectError.
        """
        if self._recv_task:
            self._recv_task.cancel()
        self._receiver.cancel()
        self._socket.close()
        self._msg_router.fail_all(DisconnectError())
