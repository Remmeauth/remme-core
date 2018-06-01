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

from remme.shared.utils import get_batch_id
from remme.account.client import AccountClient


def get(pub_key_user):
    client = AccountClient()
    address = client.make_address_from_data(pub_key_user)
    print('Reading from address: {}'.format(address))
    balance = client.get_balance(address)
    return {'balance': balance,
            'address': address}


def post(payload):
    client = AccountClient()
    address_to = client.make_address_from_data(payload['pub_key_to'])
    result = client.transfer(address_to, payload['amount'])
    return {'batch_id': get_batch_id(result)}
