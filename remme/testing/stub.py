"""
References:
    - https://remmeio.atlassian.net/wiki/spaces/WikiREMME/pages/455606289/
        2018-11-23+RFC+3+Refactoring+of+the+transaction+processors+testing+system
    - https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/
        transactions_and_batches.html#dependencies-and-input-output-addresses
    - https://github.com/hyperledger/sawtooth-core/blob/master/sdk/python/sawtooth_sdk/processor/context.py#L22
"""


class StubContext:

    def __init__(self, inputs, outputs, initial_state):
        self._state = initial_state

    def get_state(self, addresses, timeout=None):
        pass

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
