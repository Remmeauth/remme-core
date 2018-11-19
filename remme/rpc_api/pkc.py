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

from aiohttp_json_rpc import (
    RpcGenericServerDefinedError,
    RpcInvalidParamsError,
)

from remme.clients.pub_key import PubKeyClient
from remme.shared.exceptions import KeyNotFound
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
        'storage_public_key': client.get_setting_value(SETTINGS_STORAGE_PUB_KEY),
    }


async def get_public_key_info(request):
    request.params = request.params or {}
    if 'public_key' in request.params:
        try:
            public_key = request.params['public_key']
            serialization.load_pem_public_key(public_key.encode('utf-8'),
                                              default_backend())
            public_key_address = PubKeyClient() \
                .make_address_from_data(public_key)
            logger.debug(f'fetch public_key_address {public_key_address}')
        except KeyError:
            raise RpcInvalidParamsError(message='Missed public_key')
        except ValueError:
            raise RpcGenericServerDefinedError(
                error_code=-32050,
                message='Unable to load pub_key entity'
            )
    elif 'public_key_address' in request.params:
        try:
            public_key_address = request.params['public_key_address']
        except KeyError:
            raise RpcInvalidParamsError(message='Missed public_key_address')
    else:
        raise RpcInvalidParamsError(
            message='Missed public_key or public_key_address')

    client = PubKeyClient()
    try:
        pub_key_data = client.get_status(public_key_address)
        now = time.time()
        valid_from = pub_key_data.payload.valid_from
        valid_to = pub_key_data.payload.valid_to
        return {'is_revoked': pub_key_data.revoked,
                'owner_public_key': pub_key_data.owner,
                'is_valid': (not pub_key_data.revoked and valid_from < now and
                             now < valid_to),
                'valid_from': valid_from,
                'valid_to': valid_to,
                'entity_hash': pub_key_data.payload.entity_hash,
                'entity_hash_signature': pub_key_data.payload.entity_hash_signature}
    except KeyNotFound:
        raise KeyNotFound('Public key info not found')
