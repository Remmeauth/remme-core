import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.block_info import get_blocks


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_params', ['12345', True])
@pytest.mark.parametrize('key', ['start', 'limit'])
async def test_get_blocks_with_invalid_params(request_, key, invalid_params):
    """
    Case: get blocks with invalid parameter start and limit.
    Expect: incorrect parameter identifier error message.
    """
    request_.params = {
        key: invalid_params,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_blocks(request_)

    assert 'Incorrect parameter identifier.' == error.value.message
