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
from aiohttp_json_rpc.exceptions import RpcError


class RemmeRpcError(RpcError):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.message = args[0] or self.MESSAGE
        except IndexError:
            pass


class ClientException(RemmeRpcError):
    MESSAGE = 'Unhandled exception'
    ERROR_CODE = -32000


class KeyNotFound(RemmeRpcError):
    MESSAGE = 'Resource not found'
    ERROR_CODE = -32001


class ValidatorNotReadyException(RemmeRpcError):
    MESSAGE = 'Validator is not ready yet'
    ERROR_CODE = -32002


class ResourceHeaderInvalid(RemmeRpcError):
    MESSAGE = 'Invalid or missing header'
    ERROR_CODE = -32003


class InvalidResourceId(RemmeRpcError):
    MESSAGE = 'Invalid or missing resource id'
    ERROR_CODE = -32004


class CountInvalid(RemmeRpcError):
    MESSAGE = 'Invalid limit count'
    ERROR_CODE = -32005


class ResourceConsensusInvalid(RemmeRpcError):
    MESSAGE = 'Invalid or missing consensus'
    ERROR_CODE = -32006
