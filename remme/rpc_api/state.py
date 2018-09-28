import logging

from aiohttp_json_rpc import (
    RpcGenericServerDefinedError,
    RpcInvalidParamsError,
)

from remme.clients.block_info import BasicClient
from remme.shared.exceptions import ClientException, KeyNotFound


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
    try:
        return client.list_state(address, start, limit, head, reverse)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )


async def fetch_state(request):
    try:
        address = request.params['address']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed address')
    head = request.params.get('head')

    client = BasicClient()
    try:
        return client.fetch_state(address, head)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Block with id "{id}" not found'
        )
