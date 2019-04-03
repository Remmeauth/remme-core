import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.protos.node_account_pb2 import NodeAccount
from remme.rpc_api.node_account import get_node_account
from testing.utils._async import return_async_value


@pytest.mark.asyncio
async def test_get_node_account(mocker, request_):
    """
    Case: get node account data.
    Expect: dictionary with node account data.
    """
    node_account = NodeAccount()
    node_account.balance = 100
    node_account.node_state = node_account.NodeState.Value('NEW')
    node_account.reputation.frozen = 10
    node_account.reputation.unfrozen = 10

    serialize = node_account.SerializeToString()

    mock_get_block_info = mocker.patch('remme.clients.basic.BasicClient.get_value')
    mock_get_block_info.return_value = return_async_value(serialize)

    node_account_address = 'eeecb926d7a378a639a68c096ffb0bc065a692c9a4d71dd032eed8c26227ca9602adc5'

    request_.params = {
        'node_account_address': node_account_address,
    }

    result = await get_node_account(request_)

    expected_result = {
        'balance': str(node_account.balance),
        'reputation': {
            'frozen': str(node_account.reputation.frozen),
            'unfrozen': str(node_account.reputation.unfrozen),
        },
        'node_state': 'NEW',
    }

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_address', ['12345', 0, 12345, True])
async def test_get_node_account_with_invalid_address(request_, invalid_address):
    """
    Case: get node account data with invalid address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        'node_account_address': invalid_address,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_node_account(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('address_is_none', ['', None])
async def test_get_node_account_without_address(request_, address_is_none):
    """
    Case: get node account data without address.
    Expect: missed address error message.
    """
    request_.params = {
        'node_account_address': address_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_node_account(request_)

    assert 'Missed address.' == error.value.message
