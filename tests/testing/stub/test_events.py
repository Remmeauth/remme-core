"""
Provide tests for stub context events implementation.
"""
from remme.testing.stub import (
    StubContext,
    StubContextEvent,
)


def test_add_event():
    """
    Case: add event to stub context by type and attributes.
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

    assert expected_event in stub_context.events()
