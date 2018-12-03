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

from aiohttp_json_rpc import (
    RpcInvalidParamsError,
)

from remme.clients.block_info import BasicClient
from remme.shared.exceptions import KeyNotFound


__all__ = (
    'list_state',
    'fetch_state',
)

logger = logging.getLogger(__name__)


async def list_state(request):
    client = BasicClient()
    address = request.params.get('address')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    return await client.list_state(address, start, limit, head, reverse)


async def fetch_state(request):
    try:
        address = request.params['address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed address')
    head = request.params.get('head')

    client = BasicClient()
    try:
        return await client.fetch_state(address, head)
    except KeyNotFound:
        raise KeyNotFound(f'Block with id "{id}" not found')
