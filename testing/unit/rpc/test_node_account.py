import pytest

from remme.protos.account_pb2 import NodeAccount
from remme.rpc_api.account import get_node_account
from testing.utils._async import return_async_value


@pytest.mark.asyncio
async def test_get_node_account(mocker):
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

    class Request:

        @property
        def params(self):
            return {
                'node_account_address': 'eeecb926d7a378a639a68c096ffb0bc065a692c9a4d71dd032eed8c26227ca9602adc5',
            }

    request = Request()

    mock_get_block_info = mocker.patch('remme.clients.basic.BasicClient.get_value')
    mock_get_block_info.return_value = return_async_value(serialize)

    result = await get_node_account(request)

    expected_result = {
        'balance': str(node_account.balance),
        'reputation': {
            'frozen': str(node_account.reputation.frozen),
            'unfrozen': str(node_account.reputation.unfrozen),
        },
        'node_state': 'NEW',
    }

    assert expected_result == result
