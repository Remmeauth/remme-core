from remme.shared.exceptions import KeyNotFound
from connexion import NoContent


def handle_key_not_found(func):
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyNotFound:
            return NoContent, 404
    return handler
