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
import hashlib
import weakref
import re

import aiohttp

from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf import client_batch_submit_pb2
from sawtooth_sdk.messaging.exceptions import ValidatorConnectionError

from remme.shared.utils import message_to_dict

from .basic import BasicWebSocketHandler
from .constants import Action, Entity, Status
from .utils import deserialize, create_res_payload, validate_payload


LOGGER = logging.getLogger(__name__)


class WsApplicationHandler(BasicWebSocketHandler):

    def __init__(self, stream, loop):
        super().__init__(stream, loop)
        self._subscribers = []
        self._batch_ids = {}
        self._batch_update_started = False
        self._batch_updator_task = None
        self._batch_updator_task = weakref.ref(
            asyncio.ensure_future(
                self._update_list_batches(), loop=self._loop))

    async def on_shutdown(self):
        await self._unregister_subscriptions()

        self._accepting = False

        for (ws, _) in self._subscribers:
            await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

        if not self._batch_updator_task.cancelled():
            self._batch_updator_task.cancel()
        else:
            self._batch_updator_task = None
        self._batch_update_started = False

    @staticmethod
    async def _ws_send(ws, action, id=None, data=None, type='response'):
        return await ws.send_str(create_res_payload(action, data, id, type))

    async def _handle_message(self, web_sock, message_content):
        try:
            payload = deserialize(message_content)
        except Exception:
            await self._ws_send(web_sock, Status.MALFORMED_JSON)
            return

        LOGGER.info('Got payload: %s' % payload)

        err_code = validate_payload(payload)
        if err_code:
            await self._ws_send(web_sock, err_code, payload.get('id'))
            return

        try:
            action = Action(payload['action'])
        except ValueError:
            await self._ws_send(web_sock, Status.INVALID_ACTION, payload['id'])
            return

        LOGGER.info('Determined action: %s', action)

        if action == Action.SUBSCRIBE:
            await self._handle_subscribe(web_sock, payload)

        elif action == Action.UNSUBSCRIBE:
            await self._handle_unsubscribe(web_sock, payload)

    async def _update_list_batches(self, delta=5):
        self._batch_update_started = True

        async def _update_batch(batch_id):
            force_cleanup = False
            batch_data = hash_sum = None
            try:
                batch_data, hash_sum = self.get_batch(batch_id)
                LOGGER.debug('Fetched %s with sum %s', batch_data, hash_sum)
            except Exception as e:
                force_cleanup = True
                LOGGER.error('Error to get batch data: %s', e)

            batch = self._batch_ids[batch_id]

            LOGGER.debug('Got update for batch "%s"', batch)

            for ws in list(batch['ws']):
                wsdata = batch['ws'][ws]
                if ws.closed or force_cleanup:
                    LOGGER.debug('Clear connection: %s', ws)
                    self._handle_unsubscribe_batches(ws, [batch_id])
                    await self._handle_unsubscribe(ws)
                    continue

                updated, id_ = wsdata['updated'], wsdata['id']
                if updated and batch['state']['sum'] == hash_sum:
                    LOGGER.debug(f'Already updated state for conn "{ws}" '
                                 f'and batch_id "{batch_id}"')
                    continue

                try:
                    await self._ws_send(ws, Status.BATCH_RESPONSE,
                                        id_, batch_data, 'message')
                except Exception as e:
                    LOGGER.error('Send sock err: %s', e)
                    self._handle_unsubscribe_batches(ws, [batch_id])
                    await self._handle_unsubscribe(ws)
                    continue

                wsdata['updated'] = True

            batch['state']['sum'] = hash_sum
            batch['state']['data'] = batch_data

            LOGGER.debug('Batch update finish')

        while self._batch_update_started:
            LOGGER.debug('Start list batches fetching...')

            await asyncio.gather(
                *(_update_batch(batch_id)
                  for batch_id in self._batch_ids.keys()))
            await asyncio.sleep(delta)

    def _handle_subscribe_batches(self, web_sock, batch_ids, id_):
        for batch_id in batch_ids:
            batch = self._batch_ids.setdefault(batch_id, {
                'state': {
                    'sum': None,
                    'data': None
                },
                'ws': {}
            })
            batch['ws'][web_sock] = {'updated': False, 'id': id_}

    def _handle_unsubscribe_batches(self, web_sock, batch_ids):
        for batch_id in batch_ids:
            try:
                batch = self._batch_ids[batch_id]
            except KeyError:
                LOGGER.debug('Batch not found %s', batch_id)
                continue

            try:
                del batch['ws'][web_sock]
            except KeyError:
                LOGGER.debug('Ws not found in batch %s', batch_id)
                continue

            if not batch['ws']:
                del self._batch_ids[batch_id]

    async def _handle_subscribe(self, web_sock, payload):
        LOGGER.info('Sending initial most recent event to new subscriber')

        params = payload.get('parameters', {})

        try:
            entity = Entity(payload['entity'])
        except ValueError:
            await self._ws_send(web_sock, Status.INVALID_ENTITY, payload['id'])
            return

        with await self._subscriber_lock:
            if entity == Entity.BATCH_STATE:
                batch_ids = list(filter(None, params.get('batch_ids', [])))
                if not batch_ids:
                    LOGGER.debug('No batch ids on subscription')
                    await self._ws_send(web_sock, Status.INVALID_PARAMS,
                                        payload['id'])
                    return

                err_ids = self._validate_ids(batch_ids)
                if err_ids:
                    msg = 'Invalid batch ids: %s' % ', '.join(err_ids)
                    LOGGER.debug(msg)
                    await self._ws_send(web_sock, Status.INVALID_PARAMS,
                                        payload['id'])
                    return
                self._subscribers.append((web_sock, {'batch_ids': batch_ids}))
                self._handle_subscribe_batches(web_sock, batch_ids,
                                               payload['id'])
                LOGGER.info('Subscribed: %s', web_sock)

        await self._ws_send(web_sock, Status.SUBSCRIBED, payload['id'])

    async def _handle_unsubscribe(self, web_sock, payload=None):
        index = None

        with await self._subscriber_lock:
            for i, (subscriber_web_sock, _) in enumerate(self._subscribers):
                if subscriber_web_sock == web_sock:
                    index = i
                    break

            if index is not None:
                del self._subscribers[index]

            if payload is not None:
                params = payload.get('parameters', {})
                batch_ids = params.get('batch_ids', [])

                try:
                    entity = Entity(payload['entity'])
                except ValueError:
                    await self._ws_send(web_sock, Status.INVALID_ENTITY,
                                        payload['id'])
                    return

                if entity == Entity.BATCH_STATE:
                    self._handle_unsubscribe_batches(web_sock, batch_ids)
                    await self._ws_send(web_sock, Status.UNSUBSCRIBED,
                                        payload['id'])

            LOGGER.info('Unsubscribed: %s', web_sock)

    async def _handle_disconnect(self):
        LOGGER.info('Validator disconnected')
        for (ws, _) in self._subscribers:
            await self._ws_send(ws, Status.NO_VALIDATOR)

    def get_batch(self, batch_id):
        self._stream.wait_for_ready()
        future = self._stream.send(
            message_type=Message.CLIENT_BATCH_STATUS_REQUEST,
            content=client_batch_submit_pb2.ClientBatchStatusRequest(
                batch_ids=[batch_id],
            ).SerializeToString())

        try:
            resp = future.result(10).content
        except ValidatorConnectionError as vce:
            LOGGER.error('ZMQ error: %s' % vce)
            raise Exception(
                'Failed with ZMQ interaction: {0}'.format(vce))
        except asyncio.TimeoutError:
            LOGGER.error(f'Task with batch_id {batch_id} timeouted')
            raise Exception('Timeout')

        batch_resp = client_batch_submit_pb2.ClientBatchStatusResponse()
        batch_resp.ParseFromString(resp)
        LOGGER.debug(f'Batch: {resp}')
        LOGGER.info(f'Batch parsed: {batch_resp}')

        hash_sum = hashlib.sha256(batch_resp.SerializeToString()).hexdigest()
        LOGGER.debug(f'got hashsum: {hash_sum}')

        data = message_to_dict(batch_resp)
        LOGGER.debug(f'data: {data}')

        try:
            batch_data = data['batch_statuses'][0]
        except IndexError:
            raise Exception(f'Batch with id "{batch_id}" not found')

        assert batch_id == batch_data['batch_id'], \
            f'Batches not matched (req: {batch_id}, ' \
            f'got: {batch_data["batch_id"]})'

        prep_resp = {
            'batch_statuses': batch_data
        }
        return prep_resp, hash_sum

    def _validate_ids(self, ids):
        return [_id for _id in ids if not self.valid_resource_id(_id)]

    @staticmethod
    def valid_resource_id(resource_id):
        return resource_id is None or \
            bool(re.fullmatch('[0-9a-f]{128}', str(resource_id)))
