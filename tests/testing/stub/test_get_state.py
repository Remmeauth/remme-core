"""
Provide tests for stub context implementation.
"""
import pytest

from sawtooth_sdk.processor.exceptions import AuthorizationException

from remme.testing.stub import StubContext

INPUTS = ['1120...0001', '1120...0002', '1120...0003', '1120...0004']
OUTPUTS = ['1120...0003', '1120...0004', '1120...0005', '1120...0006']


def test_get_state():
    """
    Case: get state from stub context by addresses list.
    Expect: list of addresses, that match requested addresses, with its data as key-value tuple.
    """
    initial_state = {
        '1120...0001': '100',
        '1120...0002': '200',
        '1120...0003': '300',
    }

    requested_addresses = ['1120...0001', '1120...0003']

    expected_state = [
        ('1120...0001', '100'),
        ('1120...0003', '300'),
    ]

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
    assert expected_state == stub_context.get_state(addresses=requested_addresses)


def test_get_state_not_input_address():
    """
    Case: get state from stub context by addresses list with address isn't presented in inputs.
    Expect: AuthorizationError is raised.
    """
    initial_state = {
        '1120...0001': '100',
        '1120...0002': '200',
        '1120...0003': '300',
    }

    requested_addresses = ['1120...0001', '1120...0003', '1120...0005']

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)

    with pytest.raises(AuthorizationException) as error:
        stub_context.get_state(addresses=requested_addresses)

    assert 'Tried to get unauthorized address: {}'.format(requested_addresses) == str(error.value)


def test_get_state_address_data_none():
    """
    Case: get state from stub context by addresses list where some address data is None.
    Expect: list of addresses, excluding one where data is None, with its data as key-value tuple.
    """
    requested_addresses = ['1120...0001', '1120...0003', '1120...0004']

    expected_state = [
        ('1120...0001', '100'),
        ('1120...0003', '300'),
    ]

    initial_state = {
        '1120...0001': '100',
        '1120...0002': '200',
        '1120...0003': '300',
        '1120...0004': None,
    }

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state=initial_state)
    assert expected_state == stub_context.get_state(addresses=requested_addresses)
