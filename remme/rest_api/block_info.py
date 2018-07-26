
from remme.clients.block_info import BlockInfoClient
from remme.rest_api import handle_key_not_found
from remme.shared.utils import from_proto_to_dict

block_info_client = BlockInfoClient()


@handle_key_not_found
def get_block_config():
    block_config = block_info_client.get_block_info_config()
    block_config.oldest_block += 1
    block_config.latest_block += 1
    return from_proto_to_dict(block_config)


@handle_key_not_found
def get_block_info(start=None, limit=None):
    return [interpret_block_info(block) for block in block_info_client.get_many_block_info(start, limit)]


def interpret_block_info(block_info):
    return {"block_num": block_info.block_num + 1,
            "timestamp": block_info.timestamp}
