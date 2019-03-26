import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.transaction import (
    get_batch_status,
    list_batches
)
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

@pytest.mark.asyncio
@pytest.mark.parametrize('ids', [[1], [None], ['123']])
async def test_list_batches_with_invalid_ids(request_, ids):
    """
    Case: list batches with invalid ids.
    Expect: exception with invalid identifier message is raised.
    """
    request_.params = {
        'ids': ids,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Incorrect identifier.' == error.value.message or 'Missed ids' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('start', [1, '1', None])
async def test_list_batches_with_invalid_start(request_, start):
    """
    Case: list batches with invalid start field.
    Expect: exception with resource not found message is raised.
    """
    request_.params = {
        'ids': ['9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f'],
        'start': start,
        'limit': 1,
        'head': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'reverse': True
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    if start is not None:
        assert 'Given batch id is not a valid.' == error.value.message
    else:
        assert 'Missed id.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [-1, None,])
async def test_list_batches_with_invalid_limit(request_, limit):
    """
    Case: list batches with invalid limit field.
    Expect: exception with invalid limit is raised.
    """
    request_.params = {
        'ids': ['9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f'],
        'start': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'limit': limit,
        'head': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'reverse': True
    }

    with pytest.raises(Exception) as error:
        await list_batches(request_)

    assert 'Invalid limit field.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('head', [1, '1', None])
async def test_list_batches_with_invalid_head(request_, head):
    """
    Case: list batches with invalid start field.
    Expect: exception with resource not found message is raised.
    """
    request_.params = {
        'ids': ['9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f'],
        'start': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'limit': 1,
        'head': head,
        'reverse': True
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    if head is not None:
        assert 'Given batch id is not a valid.' == error.value.message
    else:
        assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('reverse', [None])
async def test_list_batches_with_invalid_reverse(request_, reverse):
    """
    Case: list batches with invalid reverse field.
    Expect: exception invalid reverse field message is raised.
    """
    request_.params = {
        'ids': ['9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f'],
        'start': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'limit': 1,
        'head': '9326f7cc285099feb39ac40058e4cdc29fa816452cee3d70dee5e7386ff61f40571e87bb1197755c246517c368d1aa89b37d4ddf52dc2d499a80f5b23ebb947f',
        'reverse': reverse
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid reverse field.' == error.value.message
