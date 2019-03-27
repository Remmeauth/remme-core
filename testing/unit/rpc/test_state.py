import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.state import (
    fetch_state,
    list_state,
)
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)


@pytest.mark.asyncio
async def test_fetch_state(mocker, request_):
    """
    Case: fetch state.
    Expect: particular leaf from the current state is fetched.
    """
    public_key_address = '112007081971dec92814033df35188ce17c740d5e58d7632c9528b61a88a4b4cde51e1'

    expected_result = {
        'head': '6213af534af2839b42005ae9e7370175e07fd69227287e9e21ad4fc513e76395'
                '4354bb2253c8d213392ea0ed47a54f8dc11bb2b6e45577fb9ffec40a22c5b043',
        'data': 'CBQ=',
    }

    mock_fetch_state = mocker.patch('remme.shared.router.Router.fetch_state')
    mock_fetch_state.return_value = return_async_value(expected_result)

    request_.params = {
        'address': public_key_address,
    }

    result = await fetch_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_public_key_address', ['12345', 0, 12345, True])
async def test_fetch_state_with_invalid_address(request_, invalid_public_key_address):
    """
    Case: fetch state with invalid address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'address': invalid_public_key_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_state(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('address_is_none', ['', None])
async def test_fetch_state_without_address(request_, address_is_none):
    """
    Case: fetch state without address.
    Expect: missed address error message.
    """
    request_.params = {
        'address': address_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_state(request_)

    assert 'Missed address.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_state_with_non_existing_address(mocker, request_):
    """
    Case: fetch state with a non-existing address.
    Expect: block for address not found error message.
    """
    invalid_address = '112007081971dec92814033df35188ce17c740d5e58d7632c9528b61a88a4b4cde51e2'
    request_.params = {
        'address': invalid_address,
    }

    expected_error_message = f'Block for address `{invalid_address}` not found.'

    mock_fetch_state = mocker.patch('remme.shared.router.Router.fetch_state')
    mock_fetch_state.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await fetch_state(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_fetch_state_with_wrong_key(request_):
    """
    Case: fetch state with wrong key.
    Expect: wrong params keys error message.
    """
    request_.params = {
        'id': '11200759ba9b0d7ff93a3a8f6eb8e25fb5802d7caa8fad3d8bc19112b82f802a0cf9e7',
    }

    expected_error_message = "Wrong params keys: ['id']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_state(request_)

    assert expected_error_message == error.value.message


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
