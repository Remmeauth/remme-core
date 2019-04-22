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
import json
import warnings
from enum import IntEnum

from google.protobuf.message import DecodeError
from google.protobuf.text_format import ParseError
from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

from remme.protos.transaction_pb2 import TransactionPayload
from remme.protos.account_pb2 import Account
from remme.protos.node_account_pb2 import NodeAccount
from remme.protos.consensus_account_pb2 import ConsensusAccount
from remme.shared.utils import hash512, Singleton, message_to_dict, client_to_real_amount
from remme.shared.metrics import METRICS_SENDER
from remme.clients.block_info import BlockInfoClient, CONFIG_ADDRESS
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.settings import TRANSACTION_FEE

from .context import CacheContextService


LOGGER = logging.getLogger(__name__)

# Key flag for transaction processor to emit event
EMIT_EVENT = 'emit_event'
PB_CLASS = 'pb_class'
PROCESSOR = 'processor'
VALIDATOR = 'validator'
FEE_AUTO_CHARGER = 'fee_auto_charger'


def is_address(address):
    try:
        assert isinstance(address, str)
        assert len(address) == 70
        int(address, 16)
        return True
    except (AssertionError, ValueError):
        return False


def add_event(context, event_type, attributes):
    context.add_event(
        event_type=event_type,
        attributes=attributes)


def get_event_attributes(updated_state, header_signature):
    entities_changed_list = [{**{
                                    'address': key,
                                    'type': value.__class__.__name__
                                 },
                              **message_to_dict(value)}
                              for key, value in updated_state.items()]
    content_dict = {"entities_changed": json.dumps(entities_changed_list),
                    "header_signature": header_signature}
    return [(key, str(value)) for key, value in content_dict.items()]


def get_data(context, pb_class, address):
    data = get_multiple_data(context, [(address, pb_class)])
    try:
        return next(data)
    except StopIteration:
        pass


def get_multiple_data(context, data):
    return context.get_cached_data(data)


class BasicHandler(metaclass=Singleton):
    """BasicHandler contains shared logic...
    """

    def __init__(self, name, versions):
        self._family_name = name
        self._family_versions = versions
        self._prefix = hash512(self._family_name)[:6]
        self._fee_address = None

    @property
    def family_name(self):
        """
           BasicHandler contains shared logic...
        """
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._prefix]

    def get_state_processor(self):
        raise InternalError('No implementation for `get_state_processor`')

    def get_message_factory(self, signer=None):
        return MessageFactory(
            family_name=self.family_name,
            family_version=self.family_versions[-1],
            namespace=self.namespaces[-1],
            signer=signer
        )

    def is_handler_address(self, address):
        return is_address(address) and address.startswith(self._prefix)

    def set_fee_address(self, address):
        """Set address for fee withdraw
        """
        self._fee_address = address

    def get_fee_address(self):
        return self._fee_address

    def apply(self, transaction, context):
        """
        Accept transaction request that passed from validator.

        Validator accept not transaction request, but transaction, that have a bit another structure.
        The flow is: transaction -> RPC -> validator -> (transaction request) handler's apply method.

        Arguments:
            transaction (sawtooth_sdk.protobuf.processor_pb2.TpProcessRequest): transaction request.
            context (sawtooth_sdk.processor.context.Context): context to store and retrieve address data.

        References:
            - https://sawtooth.hyperledger.org/docs/core/releases/1.0/sdks/python_sdk/processor.html?
                highlight=apply#processor.handler.TransactionHandler.apply
            - https://sawtooth.hyperledger.org/docs/core/releases/1.0/_autogen/sdk_TP_tutorial_python.html?
                highlight=apply#transaction-processor-tutorial-python
            - https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/transactions_and_batches.html
            - https://github.com/hyperledger/sawtooth-core/blob/10a04a56ae29b5e4b38127399dc01552db500c0a/
                protos/processor.proto#L81
            - https://github.com/hyperledger/sawtooth-core/blob/master/sdk/python/sawtooth_sdk/processor/context.py
        """
        try:
            transaction_payload = TransactionPayload()
            transaction_payload.ParseFromString(transaction.payload)
        except DecodeError:
            raise InvalidTransaction('Cannot decode transaction payload.')

        state_processor = self.get_state_processor()
        try:
            processor_data = state_processor[transaction_payload.method]
            data_pb = processor_data[PB_CLASS]()
            data_pb.ParseFromString(transaction_payload.data)
            processor = processor_data[PROCESSOR]
            validator_class = processor_data[VALIDATOR]
            fee_auto_charger = processor_data[FEE_AUTO_CHARGER]
        except KeyError:
            raise InvalidTransaction(f'Invalid account method value ({transaction_payload.method}) has been set.')

        validator = validator_class.load_proto(data_pb)
        if not validator.validate():
            raise InvalidTransaction(f'Invalid protobuf data of '
                                     f'"{validator._pb_class.__name__}", '
                                     f'detailed: {validator.errors}')

        measurement = METRICS_SENDER.get_time_measurement(
            f'tp.{self._family_name}.{transaction_payload.method}'
        )

        context_service = CacheContextService(context=context)
        context_service.preload_state(transaction.header.inputs)
        updated_state = processor(context_service, transaction.header.signer_public_key, data_pb)
        if fee_auto_charger is True:
            self.set_fee_address(self.make_address_from_data(transaction.header.signer_public_key))

        if fee_auto_charger is not None:
            updated_state = self.withdraw_fee(context_service, updated_state)

        context_service.set_state({k: v.SerializeToString() for k, v in updated_state.items()})

        event_name = processor_data.get(EMIT_EVENT, None)

        if event_name:
            event_attributes = get_event_attributes(updated_state, transaction.signature)
            add_event(context_service, event_name, event_attributes)

        measurement.done()

    def make_address(self, appendix):
        address = self._prefix + appendix
        if not is_address(address):
            raise InternalError('{} is not a valid address'.format(address))
        return address

    def make_address_from_data(self, data):
        appendix = hash512(data)[:64]
        return self.make_address(appendix)

    @staticmethod
    def get_latest_block_info(context):
        block_info_config = get_data(context, BlockInfoConfig, CONFIG_ADDRESS)

        if not block_info_config:
            raise InvalidTransaction('Block config not found.')

        LOGGER.debug(f'Current latest block number: {block_info_config.latest_block + 1}')

        block_info = get_data(context, BlockInfo, BlockInfoClient.create_block_address(block_info_config.latest_block))

        if not block_info:
            raise InvalidTransaction(f'Block {block_info_config.latest_block + 1} not found.')

        LOGGER.debug(f'Block with number successfully loaded: {block_info.block_num + 1}')

        return block_info

    def withdraw_fee(self, context, updated_state=None, fee=TRANSACTION_FEE):
        from remme.tp.node_account import NodeAccountHandler
        from remme.tp.account import AccountHandler
        from remme.tp.consensus_account import ConsensusAccountHandler

        if updated_state is None:
            updated_state = {}

        sender_address = self.get_fee_address()
        if sender_address is None:
            raise InvalidTransaction("Cannot withdraw fee: sender address not set")

        payer_account_prefix = sender_address[:6]

        payer_account_pb_selector = {
            AccountHandler()._prefix: Account,
            NodeAccountHandler()._prefix: NodeAccount,
        }

        try:
            payer_account_pb_class = payer_account_pb_selector[payer_account_prefix]
        except KeyError:
            raise InvalidTransaction('Cannot withdraw fee: invalid account type')

        consensus_address = ConsensusAccountHandler.CONSENSUS_ADDRESS

        if all([
            sender_address in updated_state,
            consensus_address in updated_state
        ]):
            payer_account = updated_state[sender_address]
            consensus_account = updated_state[consensus_address]
        elif sender_address in updated_state:
            payer_account = updated_state[sender_address]
            consensus_account = get_data(context, ConsensusAccount, consensus_address)
        elif consensus_address in updated_state:
            payer_account = get_data(context, payer_account_pb_class, sender_address)
            consensus_account = updated_state[consensus_address]
        else:
            payer_account, consensus_account = get_multiple_data(context, [
                (sender_address, payer_account_pb_class),
                (consensus_address, ConsensusAccount),
            ])

        if consensus_account is None:
            raise InvalidTransaction('Consensus account not found')

        real_fee = client_to_real_amount(fee)

        if payer_account is None or payer_account.balance < real_fee:
            raise InvalidTransaction('Not enough balance to withdraw fee')

        payer_account.balance -= real_fee
        consensus_account.block_cost += real_fee

        if sender_address not in updated_state:
            updated_state[sender_address] = payer_account

        if consensus_address not in updated_state:
            updated_state[consensus_address] = consensus_account

        return updated_state
