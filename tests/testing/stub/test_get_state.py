"""
Provide tests for stub context getting state implementation.
"""
import pytest

from sawtooth_sdk.processor.exceptions import AuthorizationException

from remme.testing.stub import (
    StubContext,
    StubContextTpStateEntry,
)

INPUTS = ['1120...0001', '1120...0002', '1120...0003', '1120...0004']
OUTPUTS = ['1120...0003', '1120...0004', '1120...0005', '1120...0006']


def test_get_state():
    """
    Case: get state from stub context by addresses list.
    Expect: list of StubContextTpStateEntry objects with addresses, that match requested addresses,
            with its data as key-value tuple.
    """
    initial_state = {
        '1120...0001': '100',
        '1120...0002': '200',
        '1120...0003': '300',
    }

    requested_addresses = ['1120...0001', '1120...0003']

    expected_state = [
        StubContextTpStateEntry(address='1120...0001', data='100'),
        StubContextTpStateEntry(address='1120...0003', data='300'),
    ]

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
    stub_context_state = stub_context.get_state(addresses=requested_addresses)

    for index in range(len(expected_state)):
        assert expected_state[index].address == stub_context_state[index].address
        assert expected_state[index].data == stub_context_state[index].data

def test_get_state_not_input_address():
    """
    Case: get state from stub context by addresses list with address isn't presented in inputs.
    Expect: AuthorizationError is raised.
    """
    requested_addresses = ['1120...0001', '1120...0003', '1120...0005']

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(AuthorizationException) as error:
        stub_context.get_state(addresses=requested_addresses)

    assert f'Tried to get unauthorized address: {requested_addresses}' == str(error.value)


def test_get_state_address_data_none():
    """
    Case: get state from stub context by addresses list where some address data is None.
    Expect: list of StubContextTpStateEntry objects with addresses, excluding one where data is None,
            with its data as key-value tuple.
    """
    requested_addresses = ['1120...0001', '1120...0003', '1120...0004']

    expected_state = [
        StubContextTpStateEntry(address='1120...0001', data='100'),
        StubContextTpStateEntry(address='1120...0003', data='300'),
    ]

    initial_state = {
        '1120...0001': '100',
        '1120...0002': '200',
        '1120...0003': '300',
        '1120...0004': None,
    }

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
    stub_context_state = stub_context.get_state(addresses=requested_addresses)

    for index in range(len(expected_state)):
        assert expected_state[index].address == stub_context_state[index].address
        assert expected_state[index].data == stub_context_state[index].data
