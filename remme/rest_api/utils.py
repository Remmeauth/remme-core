import hashlib

from sawtooth_signing import create_context

from remme.shared.utils import generate_random_key, hash256


def get_random_key():
    return {'random_key': generate_random_key()}


def post_hash256(data):
    return {'hash': hash256(int(data, 16))}

