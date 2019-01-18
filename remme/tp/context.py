import functools

from google.protobuf.text_format import ParseError
from sawtooth_sdk.processor.exceptions import InternalError

from remme.settings import STATE_TIMEOUT_SEC


class CacheContextService:

    def __init__(self, context):
        self._storage = {}
        self._context = context

    def get_context(self):
        return self._context

    def _fetch_cached_storage(self, resolvers):
        for address, _ in resolvers:
            try:
                pb = self._storage[address]
            except KeyError:
                pb = None
            yield (address, pb)

    def _get_addresses_to_reload(self, resolvers):
        return [addr for addr, pb in self._fetch_cached_storage(resolvers)
                if pb is None]

    def get_cleared_data(self, resolvers, timeout=STATE_TIMEOUT_SEC):
        raw_data = self.get_state([el[0] for el in resolvers])
        raw_data = {entry.address: entry.data for entry in raw_data}
        for address, pb_class in resolvers:
            try:
                data = pb_class()
                data.ParseFromString(raw_data[address])
                yield data
            except ParseError:
                raise InternalError('Failed to deserialize data')
            except Exception:
                yield None

    def get_cached_data(self, resolvers, timeout=STATE_TIMEOUT_SEC):
        addresses_to_reload = self._get_addresses_to_reload(resolvers)
        update_required = not self._storage or addresses_to_reload

        if update_required:
            data = self.get_cleared_data(resolvers, timeout)
            self._storage.update({
                resolvers[i][0]: pb for i, pb in enumerate(data)
            })

        for address, _ in resolvers:
            yield self._storage.get(address)

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


def preload_state(resolvers):
    def _resolve_methods(handler, ctx, signer, pub):
        for pb_cls, resolver in resolvers:
            if callable(resolver):
                resolver = resolver(handler, ctx, signer, pub)
            yield (resolver, pb_cls)

    def wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(handler, ctx, signer, pub):
            resolvers = list(_resolve_methods(handler, ctx, signer, pub))
            ctx.get_cached_data(resolvers)
            return func(handler, ctx, signer, pub)
        return inner_wrapper
    return wrapper
