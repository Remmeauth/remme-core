"""
Provide tests for stub context setting state implementation.
"""
import pytest

from sawtooth_sdk.processor.exceptions import AuthorizationException

from remme.testing.stub import StubContext

INPUTS = ['1120...0001', '1120...0002', '1120...0003', '1120...0004']
OUTPUTS = ['1120...0003', '1120...0004', '1120...0005', '1120...0006']


def test_set_state():
    """
    Case: set state to the stub context by list of addresses-data as tuple.
    Expect: list of addresses that were set.
    """
    expected_result = ['1120...0006']

    expected_state = {
        '1120...0006': '1200',
    }

    requested_entries = [
        ('1120...0006', '1200'),
    ]

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    assert expected_result == stub_context.set_state(entries=requested_entries)
    assert expected_state == stub_context.state


def test_set_state_not_output_address():
    """
    Case: set state to the stub context by list of addresses-data as tuple with address isn't presented in outputs.
    Expect: AuthorizationError is raised.
    """
    requested_addresses = ['1120...0007']

    requested_entries = [
        ('1120...0007', '700'),
    ]

    stub_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(AuthorizationException) as error:
        stub_context.set_state(entries=requested_entries)

    assert 'Tried to set unauthorized address: {}'.format(requested_addresses) == str(error.value)
