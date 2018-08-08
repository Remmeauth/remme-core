from remme.clients.pub_key import PubKeyClient


def get():
    client = PubKeyClient()
    data = client.fetch_peers()
    return {'is_synced': True, 'peer_count': len(data['data'])}
