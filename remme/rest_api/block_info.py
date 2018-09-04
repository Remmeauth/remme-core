import logging
from remme.clients.block_info import BlockInfoClient
from remme.shared.utils import from_proto_to_dict
from remme.shared.exceptions import KeyNotFound

block_info_client = BlockInfoClient()
logger = logging.getLogger(__name__)


def get_block_config():
    try:
        block_config = block_info_client.get_block_info_config()
        block_config.oldest_block += 1
        block_config.latest_block += 1
    except KeyNotFound:
        return {'error': 'Block config not found'}, 404
    else:
        return from_proto_to_dict(block_config)


def get_block_info(start, limit):
    try:
        return {'blocks': block_info_client.get_blocks_info(start, limit)}
    except KeyNotFound:
        return {'error': 'Blocks not found'}, 404
