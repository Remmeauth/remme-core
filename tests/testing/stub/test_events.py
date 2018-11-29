"""
Provide tests for stub context events implementation.
"""
from remme.testing.stub import (
    StubContext,
    StubContextEvent,
)


def test_add_event():
    """
    Case: add event to the stub context by type and attributes.
    Expect: even has been added to the events list.
    """
    event_type = 'transfer'
    event_data = b'additional-information-about-the-event'
    event_attributes = [
        ('batch_id', '71cd...f636'),
        ('amount', '100'),
    ]

    expected_event = StubContextEvent(event_type=event_type, attributes=event_attributes, data=event_data)

    stub_context = StubContext(inputs=[], outputs=[], initial_state={})
    stub_context.add_event(event_type=event_type, attributes=event_attributes, data=event_data)

    single_event = stub_context.events()[0]

    assert expected_event._event_type == single_event._event_type
    assert expected_event._attributes == single_event._attributes
    assert expected_event._data == single_event._data


def test_add_event_with_attributes_none():
    """
    Case: add event to the stub context by type and attributes where the last is None.
    Expect: even has been added to the events list with attributes is empty list ([]).
    """
    event_type = 'transfer'
    event_data = b'additional-information-about-the-event'
    event_attributes = None

    expected_event_attributes = []

    stub_context = StubContext(inputs=[], outputs=[], initial_state={})
    stub_context.add_event(event_type=event_type, attributes=event_attributes, data=event_data)

    single_event = stub_context.events()[0]

    assert expected_event_attributes == single_event._attributes
