import os
from connexion.resolver import RestyResolver
from connexion.resolver import Resolution

REST_METHODS_ENV_KEY = 'REMME_REST_API_AVAILABLE_METHODS'


def access_denied_function(*args, **kwargs):
    return {'error': 'This API method is disabled by node admin'}, 403


class RestMethodsSwitcherResolver(RestyResolver):

    def __init__(self, default_module_name, rules="*", collection_endpoint_name='search'):
        self.request_path = None
        self.request_method = None
        self.allow_all_requests = rules == '*' or rules is None
        if not self.allow_all_requests:
            try:
                rules = [ '/' + rule for rule in rules ]
                self.allowed_operations = rules
            except IndexError:
                raise ValueError('Could not parse {} env var value'.format(REST_METHODS_ENV_KEY))

        super().__init__(default_module_name, collection_endpoint_name)

    def resolve(self, operation):
        if self.is_allowed_operation(operation):
            return super().resolve(operation)
        return Resolution(access_denied_function, operation.path + operation.method)

    def is_allowed_operation(self, operation):
        self.request_path = get_clear_method_path(operation.path)
        self.request_method = operation.method.upper()

        return self.allow_all_requests or self.path_and_method_allowed()

    def path_and_method_allowed(self):
        return self.request_path_allowed() \
               and (self.method_allowed_in_path())

    def method_allowed_in_path(self):
        return self.all_methods_allowed_in_path() \
               or self.request_method in self.allowed_operations[self.request_path]

    def all_methods_allowed_in_path(self):
        return '*' in self.allowed_operations[self.request_path]

    def request_path_allowed(self):
        return self.request_path in self.allowed_operations


def get_clear_method_path(path):
    return path.split('/{')[0]
