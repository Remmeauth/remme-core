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

from enum import Enum, IntEnum, unique


@unique
class Action(Enum):

    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'


@unique
class Entity(Enum):

    BATCH_STATE = 'batch_state'


@unique
class Status(IntEnum):

    SUBSCRIBED = 10
    UNSUBSCRIBED = 11

    # couldn't parse request because of invalid json format
    MALFORMED_JSON = 100

    # no action field in the request
    MISSING_ACTION = 101

    # no such action defined in the protocol
    INVALID_ACTION = 102

    # no id field in the request
    MISSING_ID = 103

    # no parameters field in the request
    MISSING_PARAMETERS = 104

    # parameters validation failed
    # (description field with a text description should be added here)
    INVALID_PARAMS = 105

    # no such entity defined in the protocol
    INVALID_ENTITY = 106

    # no such entity defined in the protocol
    MISSING_ENTITY = 107

    # the provided message id is already in use
    # (currently there is a message with the same id and no response)
    MESSAGE_ID_EXISTS = 108

    # no type field in the request
    MISSING_TYPE = 109

    # validator connection failed
    NO_VALIDATOR = 110

    BATCH_RESPONSE = 200
