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

from remme.clients.block_info import BasicClient
from remme.rpc_api.utils import validate_params
from remme.shared.exceptions import KeyNotFound
from remme.shared.forms import get_address_form


__all__ = (
    'list_state',
    'fetch_state',
)

logger = logging.getLogger(__name__)

client = BasicClient()


@validate_params(get_address_form('address'), ignore_fields=('start', 'limit', 'head', 'reverse'))
async def list_state(request):
    address = request.params.get('address')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    return await client.list_state(address, start, limit, head, reverse)


@validate_params(get_address_form('address'), ignore_fields=('head',))
async def fetch_state(request):
    address = request.params['address']
    head = request.params.get('head')

    try:
        return await client.fetch_state(address, head)
    except KeyNotFound:
        raise KeyNotFound(f'Block for address `{address}` not found.')
