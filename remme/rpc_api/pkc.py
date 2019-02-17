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
import binascii
import logging
import time

from remme.clients.pub_key import PubKeyClient
from remme.clients.account import AccountClient
from remme.shared.exceptions import KeyNotFound
from remme.shared.forms import (
    get_address_form,
    ProtoForm,
)

__all__ = (
    'get_node_config',
    'get_public_key_info',
)

logger = logging.getLogger(__name__)

client = PubKeyClient()


@validate_params(ProtoForm)
async def get_node_config(request):
    return {
        'node_public_key': PubKeyClient().get_public_key(),
        'node_address': AccountClient().get_signer_address(),
    }


@validate_params(get_address_form('public_key_address'))
async def get_public_key_info(request):
    public_key_address = request.params['public_key_address']

    try:
        pub_key_data = await client.get_status(public_key_address)

        if not pub_key_data.payload.ByteSize():
            raise KeyNotFound

        conf_name = pub_key_data.payload.WhichOneof('configuration')
        conf_payload = getattr(pub_key_data.payload, str(conf_name))

        now = time.time()
        valid_from = pub_key_data.payload.valid_from
        valid_to = pub_key_data.payload.valid_to

        return {
            'is_revoked': pub_key_data.is_revoked,
            'owner_public_key': pub_key_data.owner,
            'type': conf_name,
            'is_valid': (
                not pub_key_data.is_revoked and valid_from < now and now < valid_to
            ),
            'valid_from': valid_from,
            'valid_to': valid_to,
            'public_key': binascii.hexlify(conf_payload.key).decode('utf-8'),
            'entity_hash': pub_key_data.payload.entity_hash.decode('utf-8'),
            'entity_hash_signature': binascii.hexlify(pub_key_data.payload.entity_hash_signature).decode('utf-8'),
        }

    except KeyNotFound:
        raise KeyNotFound('Public key info not found')
