import logging

from aiohttp_json_rpc import (
    RpcInvalidParamsError,
)

from remme.clients.block_info import BasicClient
from remme.shared.exceptions import KeyNotFound


__all__ = (
    'list_state',
    'fetch_state',
)

logger = logging.getLogger(__name__)


async def list_state(request):
    client = BasicClient()
    address = request.params.get('address')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    return client.list_state(address, start, limit, head, reverse)


async def fetch_state(request):
    try:
        address = request.params['address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed address')
    head = request.params.get('head')

    client = BasicClient()
    try:
        return client.fetch_state(address, head)
    except KeyNotFound:
        raise KeyNotFound(f'Block with id "{id}" not found')
