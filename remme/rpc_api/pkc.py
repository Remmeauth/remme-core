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
import time
import logging
import binascii

from aiohttp_json_rpc import (
    RpcInvalidParamsError,
)

from remme.clients.pub_key import PubKeyClient
from remme.shared.exceptions import KeyNotFound
from remme.protos.pub_key_pb2 import NewPubKeyPayload
from remme.settings import PRIV_KEY_FILE, SETTINGS_STORAGE_PUB_KEY

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

__all__ = (
    'get_node_config',
    'get_public_key_info',
)

logger = logging.getLogger(__name__)


async def get_node_config(request):
    client = PubKeyClient()
    return {
        'node_public_key': client.get_public_key(),
        'storage_public_key': await client.get_setting_value(SETTINGS_STORAGE_PUB_KEY),
    }


async def get_public_key_info(request):
    request.params = request.params or {}
    try:
        public_key_address = request.params['public_key_address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_address')

    client = PubKeyClient()
    try:
        pub_key_data = await client.get_status(public_key_address)

        conf_name = pub_key_data.payload.WhichOneof('configuration')
        conf_payload = getattr(pub_key_data.payload, conf_name)

        now = time.time()
        valid_from = pub_key_data.payload.valid_from
        valid_to = pub_key_data.payload.valid_to
        return {'is_revoked': pub_key_data.is_revoked,
                'owner_public_key': pub_key_data.owner,
                'type': conf_name,
                'is_valid': (not pub_key_data.is_revoked and valid_from < now and
                             now < valid_to),
                'valid_from': valid_from,
                'valid_to': valid_to,
                'public_key': binascii.hexlify(conf_payload.key).decode('utf-8'),
                'entity_hash': pub_key_data.payload.entity_hash.decode('utf-8'),
                'entity_hash_signature': binascii.hexlify(pub_key_data.payload.entity_hash_signature).decode('utf-8')}
    except KeyNotFound:
        raise KeyNotFound('Public key info not found')
