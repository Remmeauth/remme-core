import logging

from remme.clients.basic import BasicClient
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.shared.exceptions import KeyNotFound

LOGGER = logging.getLogger(__name__)

NAMESPACE = '00b10c'
CONFIG_ADDRESS = NAMESPACE + '01' + '0' * 62
BLOCK_INFO_NAMESPACE = NAMESPACE + '00'


class BlockInfoClient(BasicClient):
    def __init__(self):
        super().__init__(None)

    def get_block_info(self, block_num):
        bi = BlockInfo()
        bi.ParseFromString(self.get_value(self.create_block_address(block_num)))
        return bi

    def get_many_block_info(self, start, limit):
        result = []
        if not(start and limit):
            block_config = None
            try:
                block_config = self.get_block_info_config()
            except:
                return []

            if not start:
                start = block_config.latest_block + 1

            if not limit:
                limit = start - block_config.oldest_block + 1

        if limit - start > 0:
            limit = start

        for i in range(start-limit, start):
            result += [self.get_block_info(i)]
        result.reverse()
        return result

    def get_block_info_config(self):
        bic = BlockInfoConfig()
        bic.ParseFromString(self.get_value(CONFIG_ADDRESS))
        LOGGER.info(f'get_block_info_config: {bic}')
        return bic

    def create_block_address(self, block_num):
        return BLOCK_INFO_NAMESPACE + hex(block_num)[2:].zfill(62)
