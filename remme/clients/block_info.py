import logging

from remme.clients.basic import BasicClient
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig

LOGGER = logging.getLogger(__name__)

NAMESPACE = '00b10c'
CONFIG_ADDRESS = NAMESPACE + '01' + '0' * 62
BLOCK_INFO_NAMESPACE = NAMESPACE + '00'


class BlockInfoClient(BasicClient):

    def get_block_info(self, block_num):
        bi = BlockInfo()
        bi_addr = self.create_block_address(block_num)
        bi_state = self.get_value(bi_addr)
        bi.ParseFromString(bi_state)
        return bi

    def get_blocks_info(self, start, limit):
        blocks = []
        if not (start and limit):
            block_config = None
            try:
                block_config = self.get_block_info_config()
            except Exception:
                return blocks

            if not start:
                start = block_config.latest_block + 1

            if not limit:
                limit = start - block_config.oldest_block + 1

        if limit - start > 0:
            limit = start

        for i in range(start - limit, start):
            bi = self.get_block_info(i)
            blocks.append(self.interpret_block_info(bi))

        return list(reversed(blocks))

    def get_block_info_config(self):
        bic = BlockInfoConfig()
        bic.ParseFromString(self.get_value(CONFIG_ADDRESS))
        return bic

    @staticmethod
    def create_block_address(block_num):
        return BLOCK_INFO_NAMESPACE + hex(block_num)[2:].zfill(62)

    @staticmethod
    def interpret_block_info(block_info):
        return {"block_number": block_info.block_num + 1,
                "timestamp": block_info.timestamp,
                "previous_header_signature": block_info.previous_block_id,
                "signer_public_key": block_info.signer_public_key,
                "header_signature": block_info.header_signature}
