import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.block_info import get_blocks
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)


@pytest.mark.asyncio
@pytest.mark.parametrize('valid_params', [1, None])
async def test_get_blocks_with_valid_params(mocker, request_, valid_params):
    """
    Case: get blocks with valid parameter start.
    Expect: list of blocks.
    """
    request_.params = {
        'start': valid_params,
    }

    expected_result = [
        {
            'block_number': 1,
            'timestamp': 1553529639,
            'previous_header_signature': 0000000000000000,
            'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
            'header_signature': '0d355e7612d8bac6bc24a9d92d1b80c20c09aa0b155341774429386cdb2817a6'
                                '2d59694077f0df78b9b7222a500d267395900f06ee65a1198f76e3eb15949cdd'
        }
    ]

    mock_get_value = mocker.patch('remme.clients.block_info.BlockInfoClient.get_blocks_info')
    mock_get_value.return_value = return_async_value(expected_result)

    result = await get_blocks(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_params', ['12345', True])
async def test_get_blocks_with_invalid_params(request_, invalid_params):
    """
    Case: get blocks with invalid parameter start and limit.
    Expect: incorrect parameter identifier error message.
    """
    request_.params = {
        'start': invalid_params,
        'limit': invalid_params,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_blocks(request_)

    assert 'Incorrect parameter identifier.' == error.value.message


@pytest.mark.asyncio
async def test_get_blocks_with_non_exists_params_count(mocker, request_):
    """
    Case: get blocks with invalid parameter start.
    Expect: block not found error message.
    """
    request_.params = {
        'start': 123232456789098765456,
    }

    expected_error_message = 'Blocks not found.'

    mock_get_blocks_info = mocker.patch('remme.clients.block_info.BlockInfoClient.get_blocks_info')
    mock_get_blocks_info.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await get_blocks(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_list_blocks_with_wrong_key_address(request_):
    """
    Case: get blocks with wrong key address.
    Expect: wrong params keys error message.
    """
    block = '1'
    request_.params = {
        'address': block,
    }

    expected_error_message = "Wrong params keys: ['address']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_blocks(request_)

    assert expected_error_message == error.value.message
