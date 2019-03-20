import time
from datetime import datetime, timedelta
from random import randint

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.setting_pb2 import Setting
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.node_account_pb2 import (
    NodeAccount,
    NodeAccountMethod,
    NodeAccountInternalTransferPayload,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.clients.block_info import (
    CONFIG_ADDRESS,
    BlockInfoClient,
)
from remme.settings import (
    SETTINGS_MINIMUM_STAKE,
    SETTINGS_SWAP_COMMISSION,
    SETTINGS_BLOCKCHAIN_TAX,
)
from remme.settings.helper import _make_settings_key
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from remme.tp.context import CacheContextService
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'
RANDOM_OTHER_NODES_PUBLIC_KEY = '839d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a22369'

FROZEN = 612_345
UNFROZEN = 100_000
MINIMUM_STAKE = 250_000
SWAP_COMMISSION_AMOUNT = 100
BLOCKCHAIN_TAX_AMOUNT = 0.1

NODE_ACCOUNT_ADDRESS_FROM = '116829d71fa7e120c60fb392a64fd69de891a60c667d9ea9e5d9d9d617263be6c20202'

NODE_ACCOUNT_FROM_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'

ADDRESS_TO_GET_MINIMUM_STAKE_AMOUNT = _make_settings_key(SETTINGS_MINIMUM_STAKE)
ADDRESS_TO_GET_SWAP_COMMISSION_AMOUNT = _make_settings_key(SETTINGS_SWAP_COMMISSION)
ADDRESS_TO_GET_BLOCKCHAIN_TAX_AMOUNT = _make_settings_key(SETTINGS_BLOCKCHAIN_TAX)


def get_node_blocks(blocks_per_day: int, entropy: int, time_delta: int, node_account_public_key):
    inputs = []
    state = {}
    num = blocks_per_day * time_delta
    days_delta = 1 / blocks_per_day
    block_info_config = BlockInfoConfig()
    block_info_config.oldest_block = 0
    block_info_config.latest_block = num - 1
    serialized_block_info_config = block_info_config.SerializeToString()
    block_info_config_address = CONFIG_ADDRESS
    state[block_info_config_address] = serialized_block_info_config
    latest_block_time = datetime.now()
    for i in range(num):
        delta_timestamp = latest_block_time + timedelta(hours=24*days_delta)
        latest_block_time = delta_timestamp

        block_info_address = BlockInfoClient.create_block_address(i)

        block_info = BlockInfo()
        block_info.timestamp = int(datetime.timestamp(delta_timestamp))
        block_info.block_num = i
        # block_info.block_cost = randint(999, 1999)
        block_info.block_cost = 1000

        if i % entropy == 0:
            block_info.signer_public_key = node_account_public_key
            block_info.omega = 100
            block_info.node_oldest_block_id = entropy
        else:
            block_info.signer_public_key = RANDOM_OTHER_NODES_PUBLIC_KEY + str(randint(10, 99))

        serialized_block_info = block_info.SerializeToString()
        state[block_info_address] = serialized_block_info
        inputs.extend([block_info_config_address, block_info_address])

    return inputs, state
