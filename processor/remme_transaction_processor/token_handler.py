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

from .helpers import *
from token_pb2 import Token

FAMILY_NAME = 'token'
FAMILY_VERSIONS = ['0.1']

# TODO
# 1. initialization of the token from hardcoded public key.
# 2. method

class TokenHandler(BasicHandler):
    def __init__(self):
        super().__init__(FAMILY_NAME, FAMILY_VERSIONS)

    def apply(self, transaction, context):
        super().apply(transaction, context, Token)

    def process_state(signer, method, data, state):
        pass
