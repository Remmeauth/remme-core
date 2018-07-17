
from remme.clients.block_info import BlockInfoClient
from remme.shared.utils import from_proto_to_json

block_info_client = BlockInfoClient()


def get_block_config():
    return from_proto_to_json(block_info_client.get_block_info_config())


def get_block_info(start, end):
    return [from_proto_to_json(block) for block in block_info_client.get_many_block_info(start, end)]
