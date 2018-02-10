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

import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

# TODO: think about more logging in helper functions


class BasicHandler(TransactionHandler):
    def __init__(self, name, versions):
        self._family_name = name
        self._family_versions = versions
        self._namespace_prefix = hashlib.sha512(self.FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

    @property
    def family_name(self):
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        pass

    def _make_address(self, name):
        # TODO: Consider using hash functions from `cryptography` for more consistency
        return self.prefix + hashlib.sha512(name.encode('utf-8')).hexdigest()[0:64]


    def _decode_transaction(self, transaction, transaction_pb_class):
        transaction_payload = transaction_pb_class()
        try:
            transaction_payload.ParseFromString(transaction.payload)
        except:
            raise InvalidTransaction("Invalid payload serialization")
        return transaction_payload


    def _get_data(self, context, address, data_pb_class):
        data = data_pb_class()
        raw_data = context.get_state([address])
        try:
            data.ParseFromString(raw_data[0])
        except IndexError:
            return None
        except:
            raise InternalError("Failed to deserialize data")
        return data


    def _store_data(self, context, address, data_pb_instance):
        serialized = data_pb_instance.SerializeToString()
        adresses = context.set_state({ address: serialized })
        if len(addresses) < 1:
            raise InternalError("State Error")
