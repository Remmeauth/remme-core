import logging
import asyncio
import base64

from remme.clients.basic import BasicClient
from remme.protos.block_info_pb2 import BlockInfo, BlockInfoConfig
from remme.shared.exceptions import KeyNotFound

LOGGER = logging.getLogger(__name__)

NAMESPACE = '00b10c'
CONFIG_ADDRESS = NAMESPACE + '01' + '0' * 62
BLOCK_INFO_NAMESPACE = NAMESPACE + '00'


class BlockInfoClient(BasicClient):

    async def get_block_info_states(self, block_num, limit):
        states = await self.list_state(BLOCK_INFO_NAMESPACE, start, limit)
        return states['data']
    
    def get_block_info(self, state):
        bi = BlockInfo()
        bi.ParseFromString(state)
        return bi

    async def get_blocks_info(self, start, limit):
        init_start = start or None
        init_limit = limit or None

        try:
            block_config = await self.get_block_info_config()
        except Exception:
            return []

        start = self.create_block_address(block_config.oldest_block if not init_start else start - 1)

        limit = min(block_config.latest_block if not init_limit else limit - 1, 100)

        end = min(start + limit, block_config.latest_block) + 1
        
        # get all BlockInfo from states with given start (address of BlockInfo) and limit (number of items)
        states = await self.get_block_info_states(start, limit)
        # get all Blocks from start to limit.
        # Parameter start should correspond to this pattern 0x[a-f0-9]{16}.
        # Start is address of BlockInfo which has namespace and in the ending hex from block_num. 
        # So we should:
        # 1. get last 16 value from start as we need for list_blocks start parameter
        # 2. parse to int
        # 3. add 1 for start from next block (because we don't need first block
        # 4. parse to hex and ignore "0x"
        # 5. concatenate with 16 zeros (because we need 16 symbols and we don't know what length of our hex)
        # 6. get 16 value from concatenating string.
        start_for_list_blocks = f'0000000000000000{hex(int(start[:16], 16) + 1)[2:]}'[:16]
        # We should grab next block after limit because it's need for parsing last block for limit.
        limit_for_list_blocks = limit + 1
        blocks = (await self.list_blocks(start=f'0x{start_for_list_blocks}', limit=limit_for_list_blocks, reverse=''))['data']
        
        blocks_info = []
        for index, value in enumerate(states):
            bi = self.get_block_info(value['data'])
            
            try:
                nc = bi.block_num + 1
                if nc == block_config.latest_block + 1:
                    # for last taking votes from memory
                    seal_votes = await self.get_seal_for_last_block()
                    votes = seal_votes['data']
                else:
                    # other got from next one
                    votes = blocks[index]['header']['consensus']['previous_cert_votes']
            except KeyNotFound:
                # error occured in zero block, because of non existing address,
                # block was mined through through initial deploy
                votes = []
            except Exception as e:
                LOGGER.exception(e)
                return

            self.parse_votes(votes)

            blocks_info.append(self.interpret_block_info(bi, votes))
        
        blocks_info = list(filter(None, blocks_info))

        next_ = None
        if end < block_config.latest_block + 1:
            next_ = blocks_info[0]['block_number'] + 1

        return {
            "data": list(reversed(blocks_info)),
            "paging": {
                "next": next_,
                "start": init_start,
                "limit": init_limit,
            }
        }

    @staticmethod
    def parse_votes(votes):
        for vote in votes:
            try:
                vote['message_signature'] = base64.b64decode(vote['message_signature']).hex()
                payload = vote.setdefault('message', {'payload': {}}).get('payload', {})
                payload['proposal_id'] = base64.b64decode(payload.get('proposal_id', '')).hex()
                payload['voter_id'] = base64.b64decode(payload.get('voter_id', '')).hex()
            except Exception:
                pass

    async def get_block_info_config(self):
        bic = BlockInfoConfig()
        raw_bic = await self.get_value(CONFIG_ADDRESS)
        bic.ParseFromString(raw_bic)
        return bic

    @staticmethod
    def create_block_address(block_num):
        return BLOCK_INFO_NAMESPACE + hex(block_num)[2:].zfill(62)

    @staticmethod
    def interpret_block_info(block_info, votes):
        return {
            "block_number": block_info.block_num + 1,
            "timestamp": block_info.timestamp,
            "previous_header_signature": block_info.previous_block_id,
            "signer_public_key": block_info.signer_public_key,
            "header_signature": block_info.header_signature,
            "cert_votes": votes
        }
