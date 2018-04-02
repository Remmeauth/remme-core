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

import requests
import json
from connexion import NoContent

from remme.settings import REST_API_URL


def get(batch_id):
    try:
        response = requests.get('{}/batch_statuses?id={}'.format(REST_API_URL, batch_id))
        if response.status_code == 404:
            return NoContent, 404
        response_obj = json.loads(response.text)
        return {'batch_id': batch_id,
                'status': response_obj['data'][0]['status']}
    except requests.ConnectionError:
        return {'error': 'No Sawtooth API connection'}, 500
