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
import base64

import cbor

from sawtooth_rest_api.state_delta_subscription_handler import (StateDeltaSubscriberHandler, _message_to_dict)
from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_batch_pb2

from .constants import Action, Entity, Status
from .utils import deserialize, create_res_payload, validate_payload


logger = logging.getLogger(__name__)


class WsApplicationHandler(StateDeltaSubscriberHandler):

    def __init__(self, connection, *, loop):
        super().__init__(connection)
        self._loop = loop
        self._batch_ids = {}
        self._batch_update_started = False
        self._batch_updator_task = None
        self._batch_updator_task = weakref.ref(asyncio.ensure_future(self._update_list_batches(), loop=self._loop))

    async def on_shutdown(self):
        await super().on_shutdown()
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

        logger.info('Got payload: %s' % payload)

        err_code = validate_payload(payload)
        if err_code:
            await self._ws_send(web_sock, err_code, payload.get('id'))
            return

        try:
            action = Action(payload['action'])
        except ValueError:
            await self._ws_send(web_sock, Status.INVALID_ACTION, payload['id'])
            return

        logger.info('Determined action: %s', action)

        if action == Action.SUBSCRIBE:
            await self._handle_subscribe(web_sock, payload)

        elif action == Action.UNSUBSCRIBE:
            await self._handle_unsubscribe(web_sock, payload)

    async def _update_list_batches(self, delta=5):
        self._batch_update_started = True

        async def _update_batch(batch_id):
            batch_data, hash_sum = await self._get_batch(batch_id)
            logger.debug('Fetched %s with sum %s', batch_data, hash_sum)
            batch = self._batch_ids[batch_id]

            logger.debug('Got update for batch "%s"', batch)

            for ws, wsdata in batch['ws'].items():
                updated, id_ = wsdata['updated'], wsdata['id']
                if updated and batch['state']['sum'] == hash_sum:
                    logger.debug('Already updated state for conn "%s" and batch_id "%s"',
                                 ws, batch_id)
                    continue

                await self._ws_send(ws, Status.BATCH_RESPONSE, id_, batch_data, 'message')
                wsdata['updated'] = True

            batch['state']['sum'] = hash_sum
            batch['state']['data'] = batch_data

            logger.debug('Batch update finish')

        while self._batch_update_started:
            logger.debug('Start list batches fetching...')

            await asyncio.gather(*(_update_batch(batch_id) for batch_id in self._batch_ids.keys()))
            await asyncio.sleep(delta)

    @staticmethod
    def _batch_response_parse(data):
        for tr in data['batch']['transactions']:
            tr['payload'] = cbor.loads(base64.b64decode(tr['payload']))
            tr['header'] = cbor.loads(base64.b64decode(tr['header']))

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
                logger.debug('Batch not found %s', batch_id)
                continue

            try:
                del batch['ws'][web_sock]
            except KeyError:
                logger.debug('Ws not found in batch %s', batch_id)
                continue

    async def _handle_subscribe(self, web_sock, payload):
        logger.info('Sending initial most recent event to new subscriber')

        params = payload.get('parameters', {})
        batch_ids = params.get('batch_ids', [])

        try:
            entity = Entity(payload['entity'])
        except ValueError:
            await self._ws_send(web_sock, Status.INVALID_ENTITY, payload['id'])
            return

        with await self._subscriber_lock:
            if entity == Entity.BATCH_STATE:
                batch_ids = params.get('batch_ids', [])
                err_ids = self._validate_ids(batch_ids)
                if err_ids:
                    msg = 'Invalid batch ids: %s' % ', '.join(err_ids)
                    logger.debug(msg)
                    await self._ws_send(web_sock, Status.INVALID_PARAMS,
                                        payload['id'])
                    return
                self._subscribers.append((web_sock, {'batch_ids': batch_ids}))
                self._handle_subscribe_batches(web_sock, batch_ids, payload['id'])
                logger.info('Subscribed: %s', web_sock)

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
                    await self._ws_send(web_sock, Status.INVALID_ENTITY, payload['id'])
                    return

                if entity == Entity.BATCH_STATE:
                    self._handle_unsubscribe_batches(web_sock, batch_ids)
                    await self._ws_send(web_sock, Status.UNSUBSCRIBED, payload['id'])

            logger.info('Unsubscribed: %s', web_sock)

    async def _handle_disconnect(self):
        logger.info('Validator disconnected')
        for (ws, _) in self._subscribers:
            await self._ws_send(ws, Status.NO_VALIDATOR)

    async def _get_batch(self, batch_id):
        resp = await self._connection.send(
            Message.CLIENT_BATCH_GET_REQUEST,
            client_batch_pb2.ClientBatchGetRequest(
                batch_id=batch_id,
            ).SerializeToString())

        batch_resp = client_batch_pb2.ClientBatchGetResponse()
        batch_resp.ParseFromString(resp.content)
        logger.info('Batch: %s', resp)
        logger.info('Batch parsed: %s', batch_resp)

        hash_sum = hashlib.sha256(batch_resp.SerializeToString()).hexdigest()

        data = _message_to_dict(batch_resp)
        logger.info('data: %s', data)

        batch = data.setdefault('batch', {})
        batch['header_signature'] = batch_id

        prep_resp = {
            'batch_statuses': {
                'batch_id': batch['header_signature'],
                'status': data.get('status', 'UNKNOWN'),
                'block_number': None
            }
        }
        if batch.get('header'):
            prep_resp['batch_statuses']['block_number'] = cbor.loads(base64.b64decode(batch['header']))

        return prep_resp, hash_sum

    def _validate_ids(self, ids):
        return [_id for _id in ids if not self.valid_resource_id(_id)]

    @staticmethod
    def valid_resource_id(resource_id):
        return bool(re.fullmatch('[0-9a-f]{128}', str(resource_id)))
