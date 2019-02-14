import logging

from google.protobuf.text_format import ParseError
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.protobuf import state_context_pb2

from remme.settings import STATE_TIMEOUT_SEC


logger = logging.getLogger(__name__)


class CacheContextService:

    def __init__(self, context):
        self._storage = {}
        self._context = context

    def preload_state(self, addresses):
        addresses = list(filter(lambda a: len(a) == 70, addresses))
        entries = self.get_state(addresses)
        for i, entry in enumerate(entries):
            self._storage[entry.address] = entry.data

        logger.debug(f'Stored data for addresses: {self._storage}')

    def get_cached_data(self, resolvers, timeout=STATE_TIMEOUT_SEC):
        for address, pb_class in resolvers:
            try:
                data = self._storage[address]
                logger.debug('Got loaded data for address '
                             f'"{address}": {data}')
            except KeyError:
                try:
                    data = self.get_state([address])[0].data
                    self._storage[address] = data
                    logger.debug('Got pre-loaded data for address '
                                 f'"{address}": {data}')
                except IndexError:
                    yield None
                    continue
                except Exception as e:
                    logger.exception(e)
                    raise InternalError(f'Address "{address}" does not '
                                        'have access to data')

            if data is None:
                yield data
                continue

            try:
                pb = pb_class()
                pb.ParseFromString(data)
                yield pb
            except ParseError:
                raise InternalError('Failed to deserialize data')
            except Exception as e:
                logger.exception(e)
                yield None

    def get_state(self, addresses, timeout=STATE_TIMEOUT_SEC):
        return self._context.get_state(addresses, timeout)

    def set_state(self, entries, timeout=STATE_TIMEOUT_SEC):
        return self._context.set_state(entries, timeout)

    def delete_state(self, addresses, timeout=STATE_TIMEOUT_SEC):
        return self._context.delete_state(addresses, timeout)

    def add_receipt_data(self, data, timeout=STATE_TIMEOUT_SEC):
        return self._context.add_receipt_data(data, timeout)

    def add_event(self, event_type, attributes=None, data=None,
                  timeout=STATE_TIMEOUT_SEC):
        return self._context.add_event(event_type, attributes, data, timeout)
