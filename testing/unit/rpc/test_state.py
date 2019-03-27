import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.state import list_state
from testing.utils._async import return_async_value


@pytest.mark.asyncio
async def test_list_state(mocker, request_):
    """
    Case: get list state.
    Expect: data for the current state is fetched.
    """
    address = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'

    expected_result = {
        'data': [
            {
                'address': '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                'data': 'CBQ='
            }
        ],
        'head': '2cf7f31143a38a270e8a46b938a5516100f18f5b895651330428a1a5b1b44ffb'
                '7dab26077031f9a25e76cfb7f6692127f7d5db9b127e8b6d6b83749957ac1101',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_state = mocker.patch('remme.shared.router.Router.list_state')
    mock_list_state.return_value = return_async_value(expected_result)

    request_.params = {
        'address': address,
    }

    result = await list_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_address', ['12345', 'adef46891234asdefbcc5', 0, 12345, True])
async def test_list_state_with_invalid_address(request_, invalid_address):
    """
    Case: list state with invalid address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'address': invalid_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('address_is_none', ['', None])
async def test_list_state_without_address(request_, address_is_none):
    """
    Case: list state without address.
    Expect: missed address error message.
    """
    request_.params = {
        'address': address_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Missed address.' == error.value.message


@pytest.mark.asyncio
async def test_list_state_with_wrong_key(request_):
    """
    Case: list state with wrong key.
    Expect: wrong params keys error message.
    """
    request_.params = {
        'id': '11200759ba9b0d7ff93a3a8f6eb8e25fb5802d7caa8fad3d8bc19112b82f802a0cf9e7',
    }

    expected_error_message = "Wrong params keys: ['id']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert expected_error_message == error.value.message
