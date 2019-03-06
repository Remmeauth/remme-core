"""
Provide fixtures and useful functionality for testing.
"""
import pytest
from sawtooth_signing import (
    CryptoFactory,
    create_context,
)
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


def create_signer(private_key):
    """
    Create signer object to sign transactions to verify the owner of address does operation.
    """
    private_key = Secp256k1PrivateKey.from_hex(private_key)
    return CryptoFactory(create_context('secp256k1')).new_signer(private_key)


class Request:

    def __init__(self):
        self._params = None

    @property
    def params(self):
        """
        Substitute request params getter.
        """
        return self._params

    @params.setter
    def params(self, value):
        """
        Substitute request params setter.
        """
        self._params = {
            'public_key_address': value,
        }


@pytest.fixture
def request_():
    """
    Initialize request class.
    """
    request = Request()
    return request
