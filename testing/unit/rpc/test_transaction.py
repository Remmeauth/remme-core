import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.transaction import get_batch_status
from testing.utils._async import return_async_value

BATCH_ID = 'id'


@pytest.mark.asyncio
async def test_get_batch_status_with_invalid_batch_id(mocker, request_,):
    """
    Case: get batch status by batch id.
    Expect: batch id status.
    """
    batch_id = '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977' \
               '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f5'
    expected_result = 'COMMITTED'

    mock_list_statuses = mocker.patch('remme.shared.router.Router.list_statuses')
    mock_list_statuses.return_value = return_async_value(expected_result)

    request_.params = {
        BATCH_ID: batch_id,
    }

    result = await get_batch_status(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_batch_id', ['12345', 'Invalid id', 0, 12345, True])
async def test_get_batch_status_with_invalid_batch_id(request_, invalid_batch_id):
    """
    Case: get batch status with invalid batch id.
    Expect: given batch id is not a valid error message.
    """
    request_.params = {
        BATCH_ID: invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('batch_id_is_none', ['', None])
async def test_get_batch_status_without_batch_id(request_, batch_id_is_none):
    """
    Case: get batch status without address.
    Expect: missed ids error message.
    """
    request_.params = {
        BATCH_ID: batch_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert 'Missed id.' == error.value.message
