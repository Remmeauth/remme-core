import logging
import re
from connexion.resolver import RestyResolver
from connexion.resolver import Resolution

LOGGER = logging.getLogger(__name__)


def access_denied_function(*args, **kwargs):
    return {'error': 'This API method is disabled by node admin'}, 403


class RestMethodsSwitcherResolver(RestyResolver):
    def __init__(self, default_module_name, rules="*", collection_endpoint_name='search'):
        self.allow_all_requests = rules == '*' or rules is None
        if not self.allow_all_requests:
            if isinstance(rules, dict):
                self.allowed_operations = rules
            else:
                raise ValueError(f'The set of validation rules must be a dict, got {type(rules)}.')
        super().__init__(default_module_name, collection_endpoint_name)

    def resolve(self, operation):
        is_allowed_operation = False
        if not self.allow_all_requests:
            path = re.match(r'^/?([a-z0-9_-]+)(/.*$)?', operation.path)[1]
            method = operation.method.upper()
            if path in self.allowed_operations.keys():
                allowed_operations = self.allowed_operations[path]
                if isinstance(allowed_operations, str):
                    if allowed_operations == '*' or allowed_operations == method:
                        is_allowed_operation = True
                elif isinstance(allowed_operations, list):
                    if method in allowed_operations:
                        is_allowed_operation = True
                else:
                    raise ValueError(f'Unexpected type for operation specification: {type(allowed_operations)}. Expected dict or str.')
        else:
            is_allowed_operation = True
        if is_allowed_operation:
            LOGGER.debug(f'Allowing method {operation.method.upper()} on path {operation.path}')
            return super().resolve(operation)
        LOGGER.debug(f'Disabling method {operation.method.upper()} on path {operation.path}')
        return Resolution(access_denied_function, operation.path + operation.method)

