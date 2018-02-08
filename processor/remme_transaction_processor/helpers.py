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
        self._prefix = hashlib.sha512(self.FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

    @property
    def family_name(self):
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._prefix]

    def apply(self, transaction, context, pb_class):
        signer, method, data = _decode_transaction(transaction)

        state = self.get_data(pb_class, signer, context)

        updated_state = self.process_state(signer, method, data, state)

        self.store_state(signer, updated_state, context)

    # method to modify in custom handler
    def process_state(signer, method, data, state):
        pass

    def make_address(self, signer):
        return self._prefix + signer

    def _decode_transaction(self, transaction):
        transaction_payload = SignedDataTransaction()
        try:
            transaction_payload.ParseFromString(transaction.payload)
        except:
            raise InvalidTransaction("Invalid payload serialization")
        signer = transaction.header.signer_public_key
        data = transaction_payload.data
        method = transaction_payload.method

        return signer, method, data

    def get_data(self, pb_class, signer, context):
        data = pb_class()
        data_address = self.make_address(signer)
        raw_data = context.get_state([data_address])
        try:
            data.ParseFromString(raw_data[0])
        except IndexError:
            return None, None
        except:
            raise InternalError("Failed to deserialize data")
        return data


    def store_state(self, updated_state, data_pb_instance, context):
        serialized = data_pb_instance.SerializeToString(updated_state)
        data_address = self.make_address(signer)
        adresses = context.set_state({ data_address: serialized })
        if len(addresses) < 1:
            raise InternalError("State Error")
