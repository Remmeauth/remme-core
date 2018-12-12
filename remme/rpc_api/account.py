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

from remme.clients.account import AccountClient

__all__ = (
    'get_balance',
    'get_public_keys_list',
)


logger = logging.getLogger(__name__)


async def get_balance(request):
    client = AccountClient()
    try:
        address = request.params['public_key_address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_address')
    return await client.get_balance(address)


async def get_public_keys_list(request):
    client = AccountClient()
    try:
        address = request.params['public_key_address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_address')
    return await client.get_pub_keys(address)
