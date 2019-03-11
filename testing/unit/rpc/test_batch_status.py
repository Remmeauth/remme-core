import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.transaction import get_batch_status
from testing.utils._async import return_async_value


ID = 'id'
VALID_BATCH_ID = 'b2e08b7fd6e4568db5c3f8ed25a00f610ac9f3a1fec911c026cadccb3a5a1bd4' \
                 '79da9f4e49b4eb9d28f17fefb925e64b447ab1c694e73a8871ab3120f09dd332'


ERROR_INVALID_BATCH_ID = 'Given batch identifier is invalid'
ERROR_MISSED_ID = 'Missed id'


@pytest.mark.asyncio
async def test_get_batch_status(mocker, request_):
    """
    Case: .
    Expect: .
    """
    expected_result = []

    mock_get_block_info = mocker.patch('remme.clients.basic.BasicClient.get_batch_status')
    mock_get_block_info.return_value = return_async_value(expected_result)

    request_.params = {
        ID: VALID_BATCH_ID,
    }

    result = await get_batch_status(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'invalid_batch_id',
    [
        pytest.param(0, id='batch_id=0'),
        pytest.param('0', id='batch_id="0"'),
        pytest.param(False, id='batch_id=False'),
        pytest.param('', id='batch_id=""'),
        pytest.param(None, id='batch_id=None'),
    ])
async def test_get_batch_status_with_invalid_id(request_, invalid_batch_id):
    """
    Case: .
    Expect: .
    """
    request_.params = {
        ID: invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert ERROR_INVALID_BATCH_ID == error.value.message


@pytest.mark.asyncio
async def test_get_batch_status_without_id(request_):
    """
    Case: .
    Expect: .
    """
    request_.params = {
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert ERROR_MISSED_ID == error.value.message
