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
import json
import logging
from decimal import Decimal

from google.protobuf.json_format import MessageToJson

from remme.clients.atomic_swap import AtomicSwapClient
from remme.rpc_api.utils import validate_params
from remme.shared.exceptions import KeyNotFound
from remme.shared.utils import message_to_dict, real_to_client_amount
from remme.shared.forms import (
    AtomicSwapForm,
    ProtoForm,
)

__all__ = (
    'get_atomic_swap_info',
    'get_atomic_swap_public_key',
)

LOGGER = logging.getLogger(__name__)

client = AtomicSwapClient()


@validate_params(AtomicSwapForm)
async def get_atomic_swap_info(request):
    swap_id = request.params['swap_id']

    try:
        swap_info = await client.swap_get(swap_id)
    except KeyNotFound as e:
        raise KeyNotFound(f'Atomic swap with id "{swap_id}" not found.')
    LOGGER.info(f'Get swap info: {swap_info}')

    data = message_to_dict(swap_info)
    data['amount'] = str(real_to_client_amount(Decimal(data['amount'])))
    return data


@validate_params(ProtoForm)
async def get_atomic_swap_public_key(request):
    try:
        return await client.get_pub_key_encryption()
    except KeyNotFound:
        raise KeyNotFound('Public key for atomic swap not set')
