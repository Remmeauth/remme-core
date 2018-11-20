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
from aiohttp_json_rpc import (
    RpcInvalidParamsError,
)

from remme.clients.pub_key import PubKeyClient


__all__ = (
    'set_node_key',
    'export_node_key',
)


async def set_node_key(request):
    try:
        private_key = request.params['private_key']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed private key')

    PubKeyClient.set_priv_key_to_file(private_key)
    return True


async def export_node_key(request):
    client = PubKeyClient()
    return client.get_private_key()
