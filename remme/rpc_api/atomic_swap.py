import json
import logging

from aiohttp_json_rpc import (
    RpcInvalidParamsError,
    RpcGenericServerDefinedError,
)
from google.protobuf.json_format import MessageToJson

from remme.clients.atomic_swap import AtomicSwapClient, get_swap_init_payload
from remme.shared.exceptions import KeyNotFound


__all__ = (
    'get_atomic_swap_info',
    'get_atomic_swap_public_key',
    # TODO: Comment (remove) this before release
    # 'swap_init',
)


LOGGER = logging.getLogger(__name__)


async def swap_init(request):
    client = AtomicSwapClient()
    try:
        payload = request.params['payload']
    except KeyError as e:
        raise RpcInvalidParamsError(message='Missed payload')
    payload = get_swap_init_payload(**payload)
    return client.swap_init(payload)


async def get_atomic_swap_info(request):
    client = AtomicSwapClient()
    try:
        swap_id = request.params['swap_id']
    except KeyError as e:
        raise RpcInvalidParamsError(message='Missed swap_id')

    try:
        swap_info = client.swap_get(swap_id)
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message=f'Atomic swap with id "{swap_id}" not found'
        )
    LOGGER.info(f'Get swap info {swap_info}')
    data = MessageToJson(
        swap_info, preserving_proto_field_name=True,
        including_default_value_fields=True
    )
    return json.loads(data)


async def get_atomic_swap_public_key(request):
    client = AtomicSwapClient()
    try:
        return client.get_pub_key_encryption()
    except KeyNotFound:
        raise RpcGenericServerDefinedError(
            error_code=-32050,
            message='Public key for atomic swap not set'
        )
