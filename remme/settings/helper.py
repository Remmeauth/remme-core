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

import logging
import hashlib
from functools import lru_cache


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.messaging.future import FutureTimeoutError
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction

from sawtooth_sdk.protobuf.setting_pb2 import Setting

LOGGER = logging.getLogger(__name__)


# The config namespace is special: it is not derived from a hash.
SETTINGS_NAMESPACE = '000000'

# Number of seconds to wait for state operations to succeed
STATE_TIMEOUT_SEC = 10


def _get_setting_value(context, key, default_value=None):
    address = _make_settings_key(key)
    setting = _get_setting_entry(context, address)
    for entry in setting.entries:
        if key == entry.key:
            return entry.value

    return default_value


def get_setting_from_key_value(key, value):
    setting = Setting()
    setting.entries.add(key=key, value=str(value).encode())

    return setting


def _get_setting_entry(context, address):
    setting = Setting()

    try:
        entries_list = context.get_state([address], timeout=STATE_TIMEOUT_SEC)
    except FutureTimeoutError:
        LOGGER.warning('Timeout occured on context.get_state([%s])', address)
        raise InternalError('Unable to get {}'.format(address))

    if entries_list:
        setting.ParseFromString(entries_list[0].data)

    return setting


def _to_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _first(a_list, pred):
    return next((x for x in a_list if pred(x)), None)


def _index_of(iterable, obj):
    return next((i for i, x in enumerate(iterable) if x == obj), -1)


_MAX_KEY_PARTS = 4
_ADDRESS_PART_SIZE = 16
_EMPTY_PART = _to_hash('')[:_ADDRESS_PART_SIZE]


@lru_cache(maxsize=128)
def _make_settings_key(key):
    # split the key into 4 parts, maximum
    key_parts = key.split('.', maxsplit=_MAX_KEY_PARTS - 1)
    # compute the short hash of each part
    addr_parts = [_to_hash(x)[:_ADDRESS_PART_SIZE] for x in key_parts]
    # pad the parts with the empty hash, if needed
    addr_parts.extend([_EMPTY_PART] * (_MAX_KEY_PARTS - len(addr_parts)))

    return SETTINGS_NAMESPACE + ''.join(addr_parts)