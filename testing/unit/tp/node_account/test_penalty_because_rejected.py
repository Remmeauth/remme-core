"""
Provide tests for penalty rejected masternode implementation.
"""
import pytest

from remme.protos.node_account_pb2 import NodeAccount
from remme.tp.node_account import NodeAccountHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from testing.mocks.stub import StubContext

NODE_ACCOUNT_FROM_ADDRESS = '116829' + '0abcb27dcbecb77a6ae3ae951f878cebd2fd94b07c4e21c54a49da0f57b81a65'
NODE_ACCOUNT_FROM_ADDRESS_PUBLIC_KEY = '45a514955de0808f1fa0f38319ade0052bd36de91ae024c3422e6e9222e10604'
NODE_ACCOUNT_FROM_ADDRESS_PRIVATE_KEY = '0264f55d9e971961864a36a1a974d64cd8e76a8a07feb9f6a963e8923d0406c81d'

NODE_ACCOUNT_BALANCE = 100000
NODE_ACCOUNT_BET = 10000

INPUTS = OUTPUTS = [NODE_ACCOUNT_FROM_ADDRESS]


def test_penalty():
    """
    Case:
    Expect:
    """
    node_account = NodeAccount()
    node_account.reputation.frozen = NODE_ACCOUNT_BALANCE
    serialized_node_account = node_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        NODE_ACCOUNT_FROM_ADDRESS: serialized_node_account,
    })

    expected_node_account = NodeAccount()
    expected_node_account.reputation.frozen = NODE_ACCOUNT_BALANCE - NODE_ACCOUNT_BET
    expected_serialized_node_account = expected_node_account.SerializeToString()

    expected_state = {
        NODE_ACCOUNT_FROM_ADDRESS: expected_serialized_node_account
    }

    NodeAccountHandler()._penalty_because_rejected(
        context=mock_context,
        penalty_amount=NODE_ACCOUNT_BET,
        node_account_address=NODE_ACCOUNT_FROM_ADDRESS,
    )

    state_as_list = mock_context.get_state(addresses=[NODE_ACCOUNT_FROM_ADDRESS])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_public_key_handler_store_economy_is_not_enabled():
    """
    Case:
    Expect: invalid context or address error message.
    """
    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        NodeAccountHandler()._penalty_because_rejected(
            context=mock_context,
            penalty_amount=NODE_ACCOUNT_BET,
            node_account_address=NODE_ACCOUNT_FROM_ADDRESS,
        )

    assert 'Invalid context or address.' == str(error.value)
