import logging

from aiohttp_json_rpc import (
    RpcGenericServerDefinedError,
    RpcInvalidParamsError,
)

from remme.clients.block_info import BlockInfoClient
from remme.shared.exceptions import KeyNotFound, ClientException


__all__ = (
    'get_block_number',
    'get_blocks',

    'list_blocks',
    'fetch_block',
)

logger = logging.getLogger(__name__)


async def get_block_number(request):
    try:
        block_config = BlockInfoClient().get_block_info_config()
        block_config.latest_block += 1
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Block config not found'
        )
    else:
        return block_config.latest_block


async def get_blocks(request):
    start = request.params.get('start', 0)
    limit = request.params.get('limit', 0)

    try:
        return BlockInfoClient().get_blocks_info(start, limit)
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Blocks not found'
        )


async def list_blocks(request):
    client = BlockInfoClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')
    try:
        return client.list_blocks(ids, start, limit, head, reverse)
    except ClientException as e:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Got error response from validator: {e}'
        )


async def fetch_block(request):
    try:
        id = request.params['id']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed id')

    client = BlockInfoClient()
    try:
        return client.fetch_block(id)
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
