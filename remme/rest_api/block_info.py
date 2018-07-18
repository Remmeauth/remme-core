
from remme.clients.block_info import BlockInfoClient
from remme.rest_api import handle_key_not_found
from remme.shared.utils import from_proto_to_json

block_info_client = BlockInfoClient()


@handle_key_not_found
def get_block_config():
    return from_proto_to_json(block_info_client.get_block_info_config())


@handle_key_not_found
def get_block_info(start=None, limit=None):
    return [from_proto_to_json(block) for block in block_info_client.get_many_block_info(start, limit)]
