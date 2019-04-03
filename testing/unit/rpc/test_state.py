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
async def test_list_state_with_address(mocker, request_):
    """
    Case: get list state by address.
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
    Case: list state with invalid parameter address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'address': invalid_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
async def test_list_state_with_start(mocker, request_):
    """
    Case: get list state by start.
    Expect: data for the current state is fetched.
    """
    start = '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'

    expected_result = {
        'data': [
            {
                'address': '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c',
                'data': 'COyflKWNHQ=='
            },
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
            'start': '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
        }
    }

    mock_list_state = mocker.patch('remme.shared.router.Router.list_state')
    mock_list_state.return_value = return_async_value(expected_result)

    request_.params = {
        'start': start,
    }

    result = await list_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_start', [
    '12345', 0, 12345, True, '92fa987b4f163b43d9f85641bb8ccf018022d3a9e2445e3c721e0b3cdfa83c42'
                             '65a21c74be9f6a732f75fcab1832637fa98816cd7fb43e42b9f609ffae1136fd',
])
async def test_list_state_with_invalid_start(request_, invalid_start):
    """
    Case: list state with invalid parameter start.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'start': invalid_start,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
async def test_list_state_with_limit(mocker, request_):
    """
    Case: get list state by limit.
    Expect: data for the current state is fetched.
    """
    expected_result = {
        'data': [
            {
                'address': '0000000000000000000000000000000000000000000000000000000000000000000001',
                'data': 'CAE='
            }
        ],
        'head': '2cf7f31143a38a270e8a46b938a5516100f18f5b895651330428a1a5b1b44ffb'
                '7dab26077031f9a25e76cfb7f6692127f7d5db9b127e8b6d6b83749957ac1101',
        'paging': {
            'limit': 1,
            'next': '0000007ca83d6bbb759da9cde0fb0dec1400c5034223fb6c3e825ee3b0c44298fc1c14',
            'start': None
        }
    }

    mock_list_state = mocker.patch('remme.shared.router.Router.list_state')
    mock_list_state.return_value = return_async_value(expected_result)

    request_.params = {
        'limit': 1,
    }

    result = await list_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_limit', [True, '12345'])
async def test_list_state_with_invalid_limit(request_, invalid_limit):
    """
    Case: list state with invalid parameter limit.
    Expect: invalid limit count error message.
    """
    request_.params = {
        'limit': invalid_limit,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Invalid limit count.' == error.value.message


@pytest.mark.asyncio
async def test_list_state_with_head(mocker, request_):
    """
    Case: get list state by head.
    Expect: data for the current state is fetched.
    """
    expected_result = {
        'data': [
            {
                'address': '0000000000000000000000000000000000000000000000000000000000000000000001',
                'data': 'CAE='
            },
            {
                'address': '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c',
                'data': 'COyflKWNHQ=='
            },
            {
                'address': '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                'data': 'CBQ='
            }
        ],
        'head': 'b9ca2fc89581483138386c9816341eab6c14588e362cf4a7b95ac23525223c2c'
                '50d5c55064e1e8b64cd40413b2599fc11ff88b14b6836538a7543a665fa3ee91',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_state = mocker.patch('remme.shared.router.Router.list_state')
    mock_list_state.return_value = return_async_value(expected_result)

    request_.params = {
        'head': 'b9ca2fc89581483138386c9816341eab6c14588e362cf4a7b95ac23525223c2c'
                '50d5c55064e1e8b64cd40413b2599fc11ff88b14b6836538a7543a665fa3ee91',
    }

    result = await list_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_head', ['12345', 0, 12345, True])
async def test_list_state_with_invalid_head(request_, invalid_head):
    """
    Case: list state with invalid parameter head.
    Expect: given block id is not a valid error message.
    """
    request_.params = {
        'head': invalid_head,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Given block id is not a valid.' == error.value.message


@pytest.mark.asyncio
async def test_list_state_with_reverse(mocker, request_):
    """
    Case: get list state by reverse.
    Expect: data for the current state is fetched.
    """
    expected_result = {
        'data': [
            {
                'address': '0000000000000000000000000000000000000000000000000000000000000000000001',
                'data': 'CAE='
            },
            {
                'address': '0000007ca83d6bbb759da9cde0fb0dec1400c53feb67040a5c4884e3b0c44298fc1c14',
                'data': 'CiMKHXJlbW1lLnNldHRpbmdzLmNvbW1pdHRlZV9zaXplEgIxMA=='
            },
            {
                'address': '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c',
                'data': 'COyflKWNHQ=='
            }
        ],
        'head': 'f75639f1bd8c6f312202f6ce17db078eabf3a55c1443b998d6d7f22ba752c470'
                '6712acc128e3ef23d744b52b7ba3295846efa42a3880679af824a86df4fea64f',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_state = mocker.patch('remme.shared.router.Router.list_state')
    mock_list_state.return_value = return_async_value(expected_result)

    request_.params = {
        'reverse': 'false',
    }

    result = await list_state(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_reverse', ['12345', 0, 12345, True])
async def test_list_state_with_invalid_reverse(request_, invalid_reverse):
    """
    Case: list state with invalid parameter reverse.
    Expect: incorrect reverse identifier error message.
    """
    request_.params = {
        'reverse': invalid_reverse,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_state(request_)

    assert 'Incorrect reverse identifier.' == error.value.message


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
