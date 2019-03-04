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

from google.protobuf.json_format import MessageToJson

from remme.shared.forms import get_address_form
from remme.clients.account import AccountClient
from remme.clients.basic import BasicClient
from remme.protos.account_pb2 import NodeAccount
from .utils import validate_params

__all__ = (
    'get_balance',
    'get_public_keys_list',
    'get_node_account',
)


logger = logging.getLogger(__name__)


@validate_params(get_address_form('public_key_address'))
async def get_balance(request):
    client = AccountClient()
    address = request.params['public_key_address']
    return await client.get_balance(address)


@validate_params(get_address_form('public_key_address'))
async def get_public_keys_list(request):
    client = AccountClient()
    address = request.params['public_key_address']
    return await client.get_pub_keys(address)


async def get_node_account(request):

    client = BasicClient()

    node_address = request.params['node_account_address']
    raw_account = await client.get_value(node_address)

    node_account = NodeAccount()
    node_account.ParseFromString(raw_account)

    data = MessageToJson(message=node_account, preserving_proto_field_name=True, including_default_value_fields=True)
    return json.loads(data)
