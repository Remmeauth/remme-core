import os
from connexion.resolver import RestyResolver
from connexion.resolver import Resolution

REST_METHODS_ENV_KEY = 'REMME_REST_API_AVAILABLE_METHODS'


def access_denied_function(*args, **kwargs):
    return {'error': 'This API method is disabled by node admin'}, 403


class RestMethodsSwitcherResolver(RestyResolver):

    def __init__(self, default_module_name, collection_endpoint_name='search'):
        rules = os.getenv(REST_METHODS_ENV_KEY)
        self.allow_all_methods = rules == '*' \
                              or rules == None
        if not self.allow_all_methods:
            try:
                self.allowed_operations = get_allowed_operations(rules)
            except IndexError:
                raise ValueError('Could not parse {} env var value'.format(REST_METHODS_ENV_KEY))

        super().__init__(default_module_name, collection_endpoint_name)

    def resolve(self, operation):
        if not self.allow_all_methods and not self.is_allowed_operation(operation):
            return Resolution(access_denied_function, operation.path + operation.method)
        return super().resolve(operation)

    def is_allowed_operation(self, operation):
        request_path = get_clear_method_path(operation.path)
        request_method = operation.method.upper()

        if request_path not in self.allowed_operations:
            return False

        return '*' in self.allowed_operations[request_path] \
               or request_method in self.allowed_operations[request_path]


def get_allowed_method(method_str):
    return method_str.split(':')[0]


def get_allowed_request_types(method):
    return method.split(':')[1].split(',')


def get_allowed_methods(enviroment_var):
    return enviroment_var.split(';')


def get_clear_method_path(path):
    return path.split('/{')[0]


def get_allowed_operations(rules):
    methods = get_allowed_methods(rules)

    allowed_operations = {}
    for method_str in methods:
        method = get_allowed_method(method_str)
        allowed_operations[method] = get_allowed_request_types(method_str)

    return allowed_operations
