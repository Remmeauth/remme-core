"""
Provide implementation of the stub context, the transaction context sandbox.

StubContext particularly repeat Sawtooth context, additional knowledge could be got from its documentation.

References:
    - https://remmeio.atlassian.net/wiki/spaces/WikiREMME/pages/455606289/
        2018-11-23+RFC+3+Refactoring+of+the+transaction+processors+testing+system
    - https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/
        transactions_and_batches.html#dependencies-and-input-output-addresses
    - https://github.com/hyperledger/sawtooth-core/blob/master/sdk/python/sawtooth_sdk/processor/context.py#L22
"""
from sawtooth_sdk.processor.exceptions import AuthorizationException


class StubContextEvent:
    """
    Stub context event to be particular event sandbox.
    """

    def __init__(self, event_type, attributes, data=None):
        """
        Initialize object.

        Arguments:
            event_type (str): a type of the event.
            attributes (list of (str, str) tuples or None): an event attributes.
            data (bytes or None): Additional information about the event.
        """
        self._event_type = event_type
        self._attributes = attributes
        self._data = data


class StubContextTpStateEntry:
    """
    Stub context transaction processing state entry.

    References:
        - https://github.com/hyperledger/sawtooth-core/
        blob/10a04a56ae29b5e4b38127399dc01552db500c0a/protos/state_context.proto#L24
    """

    def __init__(self, address, data):
        self._address = address
        self._data = data

    @property
    def address(self):
        return self._address

    @property
    def data(self):
        return self._data


class StubContext:
    """
    Stub context, the transaction context sandbox.
    """

    def __init__(self, inputs, outputs, initial_state):
        """
        Initialize object.

        Arguments:
            inputs (list): a list of inputs.
            outputs (list): a list of outputs.
            initial_state (dict): initial state of the context.
        """
        self.inputs = inputs
        self.outputs = outputs
        self._state = initial_state
        self._events = []

    @property
    def state(self):
        """
        Get stub context state.
        """
        return self._state

    def get_state(self, addresses):
        """
        Get a list of addresses with its data as key-value tuple from state.

        Return list of addresses:
            - if address match requested addresses;
            - excluding address when its data is None.

        Arguments:
            addresses (list): list of address to get state by.

        Raises:
            AuthorizationError: if request address isn't presented in inputs.

        Returns list of StubContextTpStateEntry objects contain addresses with its data as key-value tuple.
        """
        for address in addresses:
            if address not in self.inputs:
                raise AuthorizationException(f'Tried to get unauthorized address: {addresses}')

        response = []

        for address in addresses:
            if address in self._state and self._state.get(address) is not None:
                response.append(
                    StubContextTpStateEntry(address=address, data=self._state.get(address)),
                )

        return response

    def set_state(self, entries):
        """
        Set a list of addresses with its data as key-value tuple to state.

        Arguments:
            entries (dict): address-data as key-value.

        Raises:
            AuthorizationError: if some of entries address isn't presented in outputs.

        Returns list of addresses that were set.
        """
        response = []

        for address, data in entries.items():

            if address not in self.outputs:
                raise AuthorizationException(f'Tried to set unauthorized address: {list(entries.keys())}')

            self._state.update({
                address: data,
            })

            response.append(address)

        return response

    def add_event(self, event_type, attributes=None, data=None):
        """
        Add a new event to the events list.

        Arguments:
            event_type (str): a type of the event.
            attributes (list of (str, str) tuples or None): an event attributes.
            data (bytes or None): Additional information about the event.
        """
        if attributes is None:
            attributes = []

        event = StubContextEvent(event_type=event_type, attributes=attributes, data=data)
        self._events.append(event)

    def events(self):
        """
        Get a stub context events list.

        Returns list of the `StubContextEvent` objects.
        """
        return self._events
