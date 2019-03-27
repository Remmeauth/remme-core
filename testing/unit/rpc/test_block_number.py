import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.block_info import (
    get_blocks,
    list_blocks,
    get_block_number,
)
from remme.tp.context import CacheContextService
from remme.protos.block_info_pb2 import BlockInfoConfig
from remme.clients.block_info import CONFIG_ADDRESS
from remme.clients.block_info import BlockInfoClient
from remme.tp.account import Account
from testing.mocks.stub import StubContext
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)

BLOCK_INFO_CONFIG = BlockInfoConfig()
BLOCK_INFO_CONFIG.latest_block = 1000


@pytest.mark.asyncio
async def test_get_block_number(mocker, request_):
    """
    Case: get block number.
    Expect: latest block number + 1.
    """
    request_.params = {}

    expected_result = BLOCK_INFO_CONFIG.latest_block + 1

    mock_get_value = mocker.patch('remme.clients.block_info.BlockInfoClient.get_block_info_config')
    mock_get_value.return_value = return_async_value(BLOCK_INFO_CONFIG)

    result = await get_block_number(request_)

    assert expected_result == result


@pytest.mark.asyncio
async def test_get_block_number_with_wrong_key_id(request_):
    """
    Case: get block number with wrong key id.
    Expect: wrong params keys id error message.
    """
    request_.params = {
        'id': '12345',
    }

    expected_error_message = "Wrong params keys: ['id']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_block_number(request_)

    assert expected_error_message == error.value.message
