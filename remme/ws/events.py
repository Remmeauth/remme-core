import json
from enum import unique

import zmq
import logging
import weakref
import asyncio

from remme.protos.atomic_swap_pb2 import AtomicSwapInfo

from remme.clients.block_info import BlockInfoClient
from remme.settings import ZMQ_URL
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest, ClientEventsSubscribeResponse, ClientEventsUnsubscribeRequest
from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf.events_pb2 import EventList, EventSubscription
from google.protobuf.json_format import MessageToJson
from remme.shared.exceptions import KeyNotFound, ClientException, ValidatorNotReadyException

from remme.shared.utils import generate_random_key
from remme.ws.basic import BasicWebSocketHandler, SocketException, SAWTOOTH_BLOCK_COMMIT_EVENT_TYPE
from enum import Enum

from remme.ws.constants import Entity, Status, ATOMIC_SWAP, Events

LOGGER = logging.getLogger(__name__)


def process_event(type, attributes):
    transaction_id = None
    entities_changed = None
    data = {}
    for item in attributes:
        if item.key == 'header_signature':
            transaction_id = item.value
        if item.key == 'entities_changed':
            entities_changed = json.loads(item.value)

    if type.startswith(ATOMIC_SWAP):
        for entity in entities_changed:
            if entity['type'] == AtomicSwapInfo.__name__:
                data = entity
    if not data:
        data = entities_changed
    return transaction_id, data


def get_value_from_key(attributes, key):
    for item in attributes:
        if item.key == key:
            return item.value


class WsEventSocketHandler(BasicWebSocketHandler):
    def __init__(self, stream, loop):
        super().__init__(stream, loop)
        # events to subscribers
        LOGGER.debug(f'Starting the event socket handler.')
        self.last_block_num = None
        self._last_block_task = weakref.ref(
            asyncio.ensure_future(
                self.request_last_block(), loop=self._loop))

        LOGGER.debug(f'Received the last block num: {self.last_block_num}')
        self._events = {event.value: {} for event in Events}

        ctx = zmq.Context()
        self._socket = ctx.socket(zmq.DEALER)
        self._socket.connect(ZMQ_URL)
        LOGGER.debug(f"Connected to ZMQ")

        self._events_updator_task = weakref.ref(
            asyncio.ensure_future(
                self.listen_events(), loop=self._loop))
        self._events_collector_task = weakref.ref(
            asyncio.ensure_future(
                self.collect_msg_to_queue(), loop=self._loop))

        self._event_lock = asyncio.Lock()
        self._event_queue = {
            Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE: asyncio.Queue(),
            Message.CLIENT_EVENTS: asyncio.Queue(),
        }

    async def request_last_block(self):
        while True:
            try:
                self.last_block_num = BlockInfoClient().get_block_info_config().latest_block + 1
            except KeyNotFound:
                self.last_block_num = 0
            except ValidatorNotReadyException:
                await asyncio.sleep(5, loop=self._loop)
                continue
            break

    async def on_shutdown(self):
        await super().on_shutdown()

        if not self._last_block_task.cancelled():
            self._last_block_task.cancel()
        else:
            self._last_block_task = None

    # return what value to be mapped to web_sock
    async def subscribe(self, web_sock, entity, data):
        if entity in [Entity.EVENTS]:
            events = data.get('events', [])
            last_known_block_id = data.get('last_known_block_id', None)
            if not events:
                raise SocketException(web_sock, Status.EVENTS_NOT_PROVIDED, f"Events being subscribed are not provided")

            for event in events:
                if event not in self._events:
                    raise SocketException(web_sock, Status.WRONG_EVENT_TYPE, f"Event: {event} is not supported")
                self._events[event][web_sock] = {'is_catch_up': bool(last_known_block_id)}

            LOGGER.debug(f'Subscribing to following events: {events}')

            await self.subscribe_events(web_sock, last_known_block_id)

            return {'events': events}

    def unsubscribe(self, web_sock):
        # currently web_sock notification is based on self._subscriptions list
        for event, web_socks_dict in self._events.items():
            if web_sock in web_socks_dict:
                del web_socks_dict[web_sock]
                self._events[event] = web_socks_dict

    async def collect_msg_to_queue(self):
        while True:
            await asyncio.sleep(2)
            try:
                resp = await self._loop.run_in_executor(None, lambda: self._socket.recv_multipart(flags=zmq.NOBLOCK)[-1])
            except zmq.Again as e:
                LOGGER.debug("No message received yet")
                continue

            # Parse the message wrapper
            msg = Message()
            msg.ParseFromString(resp)

            try:
                queue = self._event_queue[msg.message_type]
            except KeyError:
                LOGGER.error("Unexpected message type")
                continue

            await queue.put(msg)

    async def subscribe_events(self, web_sock, last_known_block_id=None):
        # Setup a connection to the validator
        LOGGER.debug(f"Subscription started")

        request = ClientEventsSubscribeRequest(subscriptions=self._make_subscriptions(),
                                               last_known_block_ids=[last_known_block_id] if last_known_block_id else []).SerializeToString()

        # Construct the message wrapper
        correlation_id = generate_random_key()  # This must be unique for all in-process requests
        msg = Message(
            correlation_id=correlation_id,
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=request)

        # Send the request
        LOGGER.debug(f"Sending subscription request.")

        await self._loop.run_in_executor(None, lambda: self._socket.send_multipart([msg.SerializeToString()]))
        LOGGER.debug(f"Subscription request is sent")

        msg = await self._event_queue[Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE].get()

        LOGGER.info(f"message type {msg.message_type}")

        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            LOGGER.error(f"Skip unexpected message type")
            return

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            if response.status == ClientEventsSubscribeResponse.UNKNOWN_BLOCK:
                raise SocketException(web_sock, Status.UNKNOWN_BLOCK,
                                      f"Uknown block in: {last_known_block_id}")
            raise SocketException(web_sock, 0, "Subscription failed: Couldn't send multipart")
        LOGGER.debug(f"Successfully subscribed")

    # The following code listens for events and logs them indefinitely.
    async def check_event(self):
        LOGGER.info(f"Checking for new events...")
        if self.last_block_num is None:
            LOGGER.debug(f"Last block number not ready!")
            return

        try:
            msg = self._event_queue[Message.CLIENT_EVENTS].get_nowait()
        except asyncio.QueueEmpty:
            LOGGER.debug("No message prepared yet")
            return

        LOGGER.info(f"message type {msg.message_type}")

        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS:
            LOGGER.error("Unexpected message type")
            return

        # Parse the response
        event_list = EventList()
        event_list.ParseFromString(msg.content)

        web_socks_to_notify = {}
        LOGGER.debug(f"Received the following events list: {event_list.events}")
        block_num = None
        block_id = None
        is_event_catch_up = False
        for event in event_list.events:
            # assumed to be the first one in the list
            if event.event_type == SAWTOOTH_BLOCK_COMMIT_EVENT_TYPE:
                block_num = int(get_value_from_key(event.attributes, "block_num"))
                block_id = get_value_from_key(event.attributes, "block_id")
                is_event_catch_up = block_num <= self.last_block_num
                self.last_block_num = max(self.last_block_num, block_num)
            else:
                event_response = {}
                event_response['type'] = event.event_type
                event_response['transaction_id'], event_response['data'] = process_event(event.event_type, event.attributes)

                event = self._events[event_response['type']]
                for web_sock in event:
                    if web_sock.closed:
                        await self._handle_unsubscribe(web_sock)
                        continue

                    if is_event_catch_up and not event[web_sock]['is_catch_up']:
                        continue

                    if web_sock not in web_socks_to_notify:
                        web_socks_to_notify[web_sock] = []

                    web_socks_to_notify[web_sock] += [event_response]
                    if self.last_block_num == block_num:
                        self._events[event_response['type']][web_sock]['is_catch_up'] = False

        for web_sock, events in web_socks_to_notify.items():
            await self._ws_send_message(web_sock, {Entity.EVENTS.value: events,
                                                   "block_num": block_num,
                                                   "block_id": block_id,
                                                   "last_known_block_num": self.last_block_num})

    async def listen_events(self, delta=5):
        while True:
            LOGGER.debug('Start events fetching...')
            await self.check_event()
            await asyncio.sleep(delta)

    def _make_subscriptions(self):
        return [EventSubscription(event_type=event_name) for event_name in self._events] + \
               [EventSubscription(event_type=SAWTOOTH_BLOCK_COMMIT_EVENT_TYPE)]
