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
@pytest.mark.parametrize('ids', [[1], ['123'], 123, True, [True], [0], [''], [None]])
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

    assert 'Invalid id.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('ids', [None])
async def test_list_batches_with_missed_ids(request_, ids):
    """
    Case: list batches with invalid ids.
    Expect: exception with invalid identifier message is raised.
    """
    request_.params = {
        'ids': ids,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Missed ids.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('start', [1, '1'])
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

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('start', [None, []])
async def test_list_batches_with_missed_start(request_, start):
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

    assert 'Missed id.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [-1, None, '1', True, 0])
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

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid limit count.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('head', [1, '1', True])
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

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('head', [None, []])
async def test_list_batches_with_missed_head(request_, head):
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

    assert 'Missed id.' == error.value.message



@pytest.mark.asyncio
@pytest.mark.parametrize('reverse', [None, 1])
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

    assert 'Incorrect identifier.' == error.value.message


@pytest.mark.asyncio
async def test_list_batches_with_correct_fields(request_):
    """
    Case: list batches with invalid reverse field.
    Expect: exception invalid reverse field message is raised.
    """
    request_.params = {
        'ids':
            [
                '85f645f7f7789e9be0ac50a5e9c7eb473b779450acba4009b1c8ea885f53e14152d378d3df6e12799327e06f17257d8f7dda2254f6bb22c0a02f499b30e16366',
                '29a1d566d8691f034212df60fc53fe2ce99533ff9b8ebc07c05fcc391a3c2ca7771aaa05c1e7830898f8566c0aa1e2a87804734683bdcc9aa2f8980dc4aacede',
                '18d2372e53e33f259f82bd1661e43d0e592e253ead26b3e08a188573424ec2636fe44fceed2415244fd14067df652977c2321e9ee0e66ffba8c13c6e290dcf7f'],

    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Incorrect identifier.' == error.value.message