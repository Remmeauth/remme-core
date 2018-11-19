import logging

from aiohttp_json_rpc import (
    RpcInvalidParamsError,
)

from remme.clients.block_info import BlockInfoClient
from remme.shared.exceptions import KeyNotFound


__all__ = (
    'get_block_number',
    'get_blocks',

    'list_blocks',
    'fetch_block',
)

logger = logging.getLogger(__name__)


async def get_block_number(request):
    try:
        block_config = await BlockInfoClient().get_block_info_config()
        return block_config.latest_block + 1
    except KeyNotFound as e:
        return 0


async def get_blocks(request):
    start = request.params.get('start', 0)
    limit = request.params.get('limit', 0)

    try:
        return await BlockInfoClient().get_blocks_info(start, limit)
    except KeyNotFound:
        raise KeyNotFound('Blocks not found')


async def list_blocks(request):
    client = BlockInfoClient()
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    return await client.list_blocks(ids, start, limit, head, reverse)


async def fetch_block(request):
    try:
        id = request.params['id']
    except KeyError:
        raise RpcInvalidParamsError(message='Missed id')

    client = BlockInfoClient()
    try:
        return await client.fetch_block(id)
    except KeyNotFound:
        raise KeyNotFound(f'Block with id "{id}" not found')
