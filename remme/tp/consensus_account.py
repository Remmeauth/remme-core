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

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from remme.protos.consensus_account_pb2 import ConsensusAccount
from remme.settings import SETTINGS_GENESIS_OWNERS
from remme.settings.helper import _get_setting_value
from remme.shared.utils import hash512
from .basic import (
    PB_CLASS,
    PROCESSOR,
    VALIDATOR,
    BasicHandler,
    get_data,
    get_multiple_data
)


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'consensus_account'
FAMILY_VERSIONS = ['0.1']


class ConsensusAccountHandler(BasicHandler):

    CONSENSUS_ADDRESS = hash512(FAMILY_NAME)[:6] + '0' * 64

    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def get_state_processor(self):
        return {}
