import hashlib

from sawtooth_signing import create_context


def generate_random_key():
    return create_context('secp256k1').new_random_private_key().as_hex()


# kecak256
def hash256(data):
    return hashlib.sha3_256(data.encode('utf-8')).hexdigest()


def hash512(data):
    return hashlib.sha512(data.encode('utf-8')).hexdigest()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def attr_dict(func):
    def wrapper(data_dict):
        return func(AttrDict(data_dict))

    return wrapper

