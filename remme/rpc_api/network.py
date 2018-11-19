import logging

from remme.clients.pub_key import PubKeyClient


__all__ = (
    'get_node_info',
    'fetch_peers',
    # 'fetch_status',
)

logger = logging.getLogger(__name__)


async def get_node_info(request):
    client = PubKeyClient()
    data = await client.fetch_peers()
    return {'is_synced': True, 'peer_count': len(data['data'])}


async def fetch_peers(request):
    client = PubKeyClient()
    return await client.fetch_peers()


# async def fetch_status(request):
#     client = PubKeyClient()
#     return client.fetch_status()
