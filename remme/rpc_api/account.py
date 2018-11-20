import logging

from aiohttp_json_rpc import (
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
        address = request.params['public_key_address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_address')
    return client.get_balance(address)


async def get_public_keys_list(request):
    client = AccountClient()
    try:
        address = request.params['public_key_address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed public_key_address')
    return client.get_pub_keys(address)
