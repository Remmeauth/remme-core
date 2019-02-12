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

# pylint: disable=invalid-name
# pylint: disable=global-statement
from sawtooth_signing import create_context
from aiohttp import web

KEY_NUM = 50

num_connections = 0
context = create_context('secp256k1')
keys = [context.new_random_private_key().as_hex() for _ in range(KEY_NUM)]
ips = []


async def get_config(request):
    global num_connections, ips
    ip = request.remote
    result = {
        'privkey': keys[num_connections],
        'ip': ip,
        'peers': ','.join(ips),
    }
    ips.append(f'tcp://{ip}:8800')
    num_connections += 1
    return web.json_response(result)

app = web.Application()
app.router.add_get('/', get_config)
web.run_app(app, port=8000)
