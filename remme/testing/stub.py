"""
StubContext is ..

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
        self._event_type = event_type
        self._attributes = attributes
        self._data = data


class StubContext:

    def __init__(self, inputs, outputs, initial_state):
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

    def get_state(self, addresses, timeout=None):
        """
        Get list of addresses with its data as key-value tuple.

        Return list of addresses:
            - if address match requested addresses;
            - excluding address when its data is None.

        Arguments:
            addresses (list): list of address to get state by.

        Raises:
            AuthorizationError: if request address isn't presented in inputs.

        Returns list of addresses with its data as key-value tuple.
        """
        for address in addresses:
            if address not in self.inputs:
                raise AuthorizationException('Tried to get unauthorized address: {}'.format(addresses))

        response = []

        for address in addresses:

            if address in self._state and self._state.get(address) is not None:
                response.append(
                    (address, self._state.get(address)),
                )

        return response

    def set_state(self, entries, timeout=None):
        pass

    def add_event(self, event_type, attributes, data):
        pass

    def events(self):
        """
        Get stub context events list.

        Returns list of the `StubContextEvent` objects.
        """
        return self._events
