import logging

from aiohttp_json_rpc import (
    RpcGenericServerDefinedError,
    RpcInvalidParamsError,
)

from remme.clients.account import AccountClient

__all__ = (
    'get_balance',
    'get_public_keys_list',
)


logger = logging.getLogger(__name__)


async def get_balance(request):
    client = AccountClient()
    try:
        pub_key_user = request.params['public_key']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public key')

    try:
        address = client.make_address_from_data(pub_key_user)
    except TypeError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Invalid public key for address creation'
        )
    logger.debug('Reading from address: {}'.format(address))
    return client.get_balance(address)


async def get_public_keys_list(request):
    client = AccountClient()
    try:
        pub_key_user = request.params['public_key']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public key')

    try:
        address = client.make_address_from_data(pub_key_user)
    except TypeError:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Invalid public key for address creation'
        )
    logger.debug('Reading from address: {}'.format(address))
    return client.get_pub_keys(address)
