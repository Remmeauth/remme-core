import json

import logging
import weakref
import asyncio

from concurrent.futures import TimeoutError
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest
from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf.events_pb2 import EventList, EventSubscription
from google.protobuf.json_format import MessageToJson
from sawtooth_sdk.messaging.exceptions import ValidatorConnectionError

from remme.ws.basic import BasicWebSocketHandler
from remme.ws.constants import Entity

SWAP_INIT_EVENT = 'atomic-swap-init'

LOGGER = logging.getLogger(__name__)


class WSEventSocketHandler(BasicWebSocketHandler):
    def __init__(self, stream, loop):
        super().__init__(stream, loop)
        self._events = [SWAP_INIT_EVENT]
        self._events_updator_task = weakref.ref(
            asyncio.ensure_future(
                self.listen_events(), loop=self._loop))
        self.subscribe_events()

    # return what value to be mapped to web_sock
    def subscribe(self, entity, data):
        if entity == Entity.EVENTS:
            events = data.get('events', [])
            return {'events': events}

    def unsubscribe(self, entity, data):
        pass

    def subscribe_events(self):
        # Setup a connection to the validator
        LOGGER.info(f"Subscribing to events")

        request = ClientEventsSubscribeRequest(subscriptions=self._make_subscriptions(), last_known_block_ids=[]).SerializeToString()

        # Send the request
        LOGGER.info(f"Sending subscription request.")

        self._stream.wait_for_ready()
        future = self._stream.send(
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=request)

        try:
            resp = future.result(3).content
        except ValidatorConnectionError as vce:
            LOGGER.error('Error: %s' % vce)
            raise Exception(
                'Failed with ZMQ interaction: {0}'.format(vce))

        LOGGER.info(f'Subscription response: {resp}')
        LOGGER.info(f"Subscribed.")

    # The following code listens for events and logs them indefinitely.
    async def check_event(self):
        LOGGER.info(f"Checking for new events...")

        resp = None
        try:
            # resp = self._socket.recv_multipart(flags=zmq.NOBLOCK)[-1]
            resp = self._stream.receive().result(3).content
        except TimeoutError:
            LOGGER.info("No message received yet")
            return

        # Parse the message wrapper
        msg = Message()
        msg.ParseFromString(resp)

        LOGGER.info(f"message type {msg.message_type}")

        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS:
            LOGGER.info("Unexpected message type")
            return

        # Parse the response
        event_list = EventList()
        event_list.ParseFromString(msg.content)

        result = []
        for event in event_list.events:
            event = json.loads(
                MessageToJson(event, preserving_proto_field_name=True, including_default_value_fields=True))
            event_response = {}
            event_response['type'] = event['event_type']
            event_response['data'] = {item['key']: item['value'] for item in event['attributes']}
            result += [event_response]

        for web_sock, _ in self._subscribers.items():
            await self._ws_send_message(web_sock, {Entity.EVENTS.value: result})

    async def listen_events(self, delta=5):
        while True:
            LOGGER.debug('Start events fetching...')
            await asyncio.gather(*[self.check_event()])
            await asyncio.sleep(delta)

    def _make_subscriptions(self):
        return [EventSubscription(event_type=event_name) for event_name in self._events]
