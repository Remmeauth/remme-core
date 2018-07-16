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

import ujson

from .constants import Status


def serialize(payload):
    return ujson.dumps(payload)


def deserialize(payload):
    return ujson.loads(payload)


def create_res_payload(status, data, id, type):
    payload = {
        'type': type,
        'status': status.name.lower(),
    }
    if id:
        payload['id'] = id
    if type == 'message':
        payload['data'] = data
        del payload['status']
    if type == 'error':
        payload['description'] = data
    return serialize(payload)


def validate_payload(payload):
    if not payload.get('type'):
        return Status.MISSING_TYPE
    elif not payload.get('action'):
        return Status.MISSING_ACTION
    elif not payload.get('entity'):
        return Status.MISSING_ENTITY
    elif not payload.get('id'):
        return Status.MISSING_ID
    elif not payload.get('parameters'):
        return Status.MISSING_PARAMETERS
