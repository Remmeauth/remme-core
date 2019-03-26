import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.block_info import list_blocks


@pytest.mark.asyncio
async def test_list_blocks_with_wrong_key_address(request_):
    """
    Case: get list blocks with wrong key address.
    Expect: wrong params keys error message.
    """
    address = '11200759ba9b0d7ff93a3a8f6eb8e25fb5802d7caa8fad3d8bc19112b82f802a0cf9e7'
    request_.params = {
        'address': address,
    }

    expected_error_message = "Wrong params keys: ['address']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_blocks(request_)

    assert expected_error_message == error.value.message
