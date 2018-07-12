from remme.clients.block_info import BlockInfoClient

block_info_client = BlockInfoClient()


def get_block_config():
    return block_info_client.get_block_info_config()


def get_block_info(block_start, block_end):
    return block_info_client.get_many_block_info(block_start, block_end)
