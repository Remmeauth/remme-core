from remme.atomic_swap_tp.client import AtomicSwapClient, get_swap_init_payload, get_swap_approve_payload, \
    get_swap_expire_payload, get_swap_set_secret_lock_payload, get_swap_close_payload

client = AtomicSwapClient()


def init(data):
    payload = get_swap_init_payload(data)
    return client.swap_init(payload)


def approve(data):
    payload = get_swap_approve_payload(data)
    return client.swap_approve(payload)


def expire(data):
    payload = get_swap_expire_payload(data)
    return client.swap_expire(payload)


def set_secret_lock(data):
    payload = get_swap_set_secret_lock_payload(data)
    return client.swap_set_secret_lock(payload)


def close(data):
    swap_info = get_swap_info(data.swap_id)
    payload = get_swap_close_payload(data)
    return client.swap_close(payload, receiver_address=swap_info.receiver_address)


def get_swap_info(swap_id):
    return client.swap_get(swap_id)


# approve
# expire
# set-secret-lock
# close
#
# def approve(data):
#     payload = get_swap_approve_payload(data)
#     return AtomicSwapClient().swap_init(payload)
