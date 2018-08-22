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

import toml


def _merge_deep(a, b):
    common = list(set(a.keys()) & set(b.keys()))
    merged = {**a, **b}
    for key in common:
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            merged[key] = _merge_deep(a[key], b[key])
    return merged


def load_toml_with_defaults(filename, subpath=None, defaults=None):
    value = toml.load(filename)
    if isinstance(subpath, list):
        for key in subpath:
            value = value[key]
    if isinstance(defaults, dict):
        value = _merge_deep(defaults, value)
    return value

DEFAULT_CLIENT_CONFIG = {
    'validator_ip': '127.0.0.1',
    'validator_port': 4004,
    'validator_rest_api_url': 'http://127.0.0.1:8008',
}

DEFAULT_GENESIS_CONFIG = {
    'token_supply': 1000000000000,
    'economy_enabled': True,
    'consensus': 'poet-simulator',
}

DEFAULT_REST_API_CONFIG = {
    'bind': '0.0.0.0',
    'port': 8080,
    'exports_folder': './default_export',
    'available_methods': '*',
    'allow_origin': '*',
    'expose_headers': '*',
    'allow_headers': '*',
    'allow_methods': ['GET', 'POST', 'PUT', 'DELETE'],
    'max_age': 10000,
    'allow_credentials': False,
}

