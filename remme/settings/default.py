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

import logging
import toml
from pkg_resources import resource_filename

LOGGER = logging.getLogger(__name__)


def _merge_deep(a, b):
    common = list(set(a.keys()) & set(b.keys()))
    merged = {**a, **b}
    for key in common:
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            merged[key] = _merge_deep(a[key], b[key])
    return merged


def load_toml_with_defaults(filename):
    defaults = toml.load(resource_filename(__name__, 'default_config.toml'))
    try:
        value = toml.load(filename)
        value = _merge_deep(defaults, value)
        return value
    except IOError:
        LOGGER.warning(f'Configuration file {filename} not found, reverting to defaults.')
        return defaults
