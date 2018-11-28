"""
References:
    - https://remmeio.atlassian.net/wiki/spaces/WikiREMME/pages/455606289/
        2018-11-23+RFC+3+Refactoring+of+the+transaction+processors+testing+system
    - https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/
        transactions_and_batches.html#dependencies-and-input-output-addresses
    - https://github.com/hyperledger/sawtooth-core/blob/master/sdk/python/sawtooth_sdk/processor/context.py#L22
"""
from sawtooth_sdk.processor.exceptions import AuthorizationException


class StubContext:

    def __init__(self, inputs, outputs, initial_state):
        self.inputs = inputs
        self.outputs = outputs
        self._state = initial_state

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

    def delete_state(self, adresses, timeout=None):
        pass

    def add_receipt_data(self, data, timeout=None):
        pass

    def add_event(self, event_type, attributes, data):
        pass

    @property
    def state(self):
        pass

    def events(self):
        pass
