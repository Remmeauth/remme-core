from remme.atomic_swap_tp.client import AtomicSwapClient, get_swap_init_payload


def init(data):
    client = AtomicSwapClient()
    payload = get_swap_init_payload(data)
    return client.swap_init(payload)
