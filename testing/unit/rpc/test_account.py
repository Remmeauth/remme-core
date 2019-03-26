import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.account import (
    get_balance,
    get_public_keys_list,
)
from testing.utils._async import return_async_value

PUBLIC_KEY_ADDRESS = 'public_key_address'


@pytest.mark.asyncio
async def test_get_balance(mocker, request_):
    """
    Case: get balance.
    Expect: list with addresses.
    """
    public_key_address = '112007081971dec92814033df35188ce17c740d5e58d7632c9528b61a88a4b4cde51e1'
    expected_result = 1000

    mock_get_block_info = mocker.patch('remme.clients.account.AccountClient.get_balance')
    mock_get_block_info.return_value = return_async_value(expected_result)

    request_.params = {
        'public_key_address': public_key_address,
    }

    result = await get_balance(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_public_key_address', ['12345', 0, 12345, True])
async def test_get_balance_with_invalid_address(request_, invalid_public_key_address):
    """
    Case: get balance with invalid address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'public_key_address': invalid_public_key_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_balance(request_)

    assert {
        'public_key_address': ['Address is not of a blockchain token type.'],
    } == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('address_is_none', ['', None])
async def test_get_balance_without_address(request_, address_is_none):
    """
    Case: get balance without address.
    Expect: missed address error message.
    """
    request_.params = {
        'public_key_address': address_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_balance(request_)

    assert {
        'public_key_address': ['Missed address.'],
    } == error.value.message


@pytest.mark.asyncio
async def test_get_balance_excess_parameters(request_):
    """
    Case: get balance without address.
    Expect: missed address error message.
    """
    request_.params = {
        'some_excess_parameter': 567890,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_balance(request_)

    assert {
        'error': ["Wrong params keys: ['some_excess_parameter']"]
    } == error.value.message


@pytest.mark.asyncio
async def test_get_public_keys_list(mocker, request_):
    """
    Case: get public keys list.
    Expect: list with addresses.
    """
    public_key_address = '112007081971dec92814033df35188ce17c740d5e58d7632c9528b61a88a4b4cde51e1'
    expected_result = []

    mock_get_block_info = mocker.patch('remme.clients.account.AccountClient.get_pub_keys')
    mock_get_block_info.return_value = return_async_value(expected_result)

    request_.params = {
        PUBLIC_KEY_ADDRESS: public_key_address,
    }

    result = await get_public_keys_list(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_public_key_address', ['12345', 0, 12345, True])
async def test_get_public_keys_list_with_invalid_address(request_, invalid_public_key_address):
    """
    Case: get public keys list with invalid address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        PUBLIC_KEY_ADDRESS: invalid_public_key_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_public_keys_list(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('address_is_none', ['', None])
async def test_get_public_keys_list_without_address(request_, address_is_none):
    """
    Case: get public keys list without address.
    Expect: missed address error message.
    """
    request_.params = {
        PUBLIC_KEY_ADDRESS: address_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_public_keys_list(request_)

    assert 'Missed address.' == error.value.message
