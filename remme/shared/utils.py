import hashlib
import binascii
import codecs

import sha3
from google.protobuf.json_format import MessageToDict
from sawtooth_signing import create_context


def generate_random_key():
    return create_context('secp256k1').new_random_private_key().as_hex()


# kecak256
def hash256(data):
    return hashlib.sha3_256(data.encode('utf-8')
                            if isinstance(data, str) else data).hexdigest()


def hash512(data):
    return hashlib.sha512(data.encode('utf-8')
                          if isinstance(data, str) else data).hexdigest()


def remove_0x_prefix(value):
    if value.startswith('0x'):
        return value[2:]
    return value


def web3_hash(data):
    if len(data) % 2:
        data = '0x0' + remove_0x_prefix(data)

    data = codecs.decode(remove_0x_prefix(data), 'hex')
    return sha3.keccak_256(data).hexdigest()


def from_proto_to_dict(proto_obj):
    return MessageToDict(proto_obj, preserving_proto_field_name=True,
                         including_default_value_fields=True)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_batch_id(response_dict):
    link = response_dict['link']
    batch_id = link.split('id=')[1]
    return {'batch_id': batch_id}


def message_to_dict(message):
    return MessageToDict(
        message,
        including_default_value_fields=True,
        preserving_proto_field_name=True)


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls) \
                .__call__(*args, **kwargs)
        return cls._instances[cls]
