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

from remme.clients.pub_key import PubKeyClient


__all__ = (
    'get_node_info',
    'fetch_peers',
    # 'fetch_status',
)

logger = logging.getLogger(__name__)


async def get_node_info(request):
    client = PubKeyClient()
    data = await client.fetch_peers()
    return {'is_synced': True, 'peer_count': len(data['data'])}


async def fetch_peers(request):
    client = PubKeyClient()
    return await client.fetch_peers()


# async def fetch_status(request):
#     client = PubKeyClient()
#     return client.fetch_status()
