import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError
from datetime import datetime

from remme.protos.atomic_swap_pb2 import AtomicSwapInfo
from remme.rpc_api.atomic_swap import get_atomic_swap_info
from remme.shared.exceptions import KeyNotFound
from remme.shared.utils import client_to_real_amount, real_to_client_amount
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)

SWAP_ID = 'swap_id'


@pytest.mark.asyncio
async def test_get_atomic_swap_info(mocker, request_):
    """
    Case: get atomic swap information.
    Expect: information in json format.
    """
    atomic_swap_info = AtomicSwapInfo()
    atomic_swap_info.state = atomic_swap_info.State.Value('OPENED')
    atomic_swap_info.sender_address = '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
    atomic_swap_info.sender_address_non_local = '0xe6ca0e7c974f06471759e9a05d18b538c5ced11e'
    atomic_swap_info.receiver_address = '112007484def48e1c6b77cf784aeabcac51222e48ae14f3821697f4040247ba01558b1'
    atomic_swap_info.amount = client_to_real_amount(10)
    atomic_swap_info.email_address_encrypted_optional = ''
    atomic_swap_info.swap_id = '133102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3806'
    atomic_swap_info.secret_key = ''
    atomic_swap_info.secret_lock = 'b605112c2d7489034bbd7beab083fb65ba02af787786bb5e3d99bb26709f4f68'
    atomic_swap_info.created_at = int(datetime.now().timestamp())
    atomic_swap_info.is_initiator = False

    serialize = atomic_swap_info.SerializeToString()

    mock_get_value = mocker.patch('remme.clients.basic.BasicClient.get_value')
    mock_get_value.return_value = return_async_value(serialize)

    swap_id = '133102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3806'

    request_.params = {
        SWAP_ID: swap_id,
    }

    result = await get_atomic_swap_info(request_)

    expected_result = {
        'amount': str(real_to_client_amount(atomic_swap_info.amount)),
        'created_at': atomic_swap_info.created_at,
        'email_address_encrypted_optional': str(atomic_swap_info.email_address_encrypted_optional),
        'is_initiator': atomic_swap_info.is_initiator,
        'receiver_address': str(atomic_swap_info.receiver_address),
        'secret_key': str(atomic_swap_info.secret_key),
        'secret_lock': str(atomic_swap_info.secret_lock),
        'sender_address': str(atomic_swap_info.sender_address),
        'sender_address_non_local': str(atomic_swap_info.sender_address_non_local),
        'state': 'OPENED',
        'swap_id': str(atomic_swap_info.swap_id)
    }

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_swap_id', [
    '12345', '133102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce38zz', 0, 12345, True,
])
async def test_get_atomic_swap_info_with_invalid_swap_id(request_, invalid_swap_id):
    """
    Case: get atomic swap info with invalid swap id.
    Expect: given swap id is not a valid error message.
    """
    request_.params = {
        SWAP_ID: invalid_swap_id
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_atomic_swap_info(request_)

    assert 'Given swap_id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('swap_id_is_none', ['', None])
async def test_get_atomic_swap_info_without_swap_id(request_, swap_id_is_none):
    """
    Case: get atomic swap info without swap id.
    Expect: missed swap id error message.
    """
    request_.params = {
        SWAP_ID: swap_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_atomic_swap_info(request_)

    assert 'Missed swap_id.' == error.value.message


@pytest.mark.asyncio
async def test_get_atomic_swap_info_with_non_existing_swap_id(mocker, request_):
    """
    Case: get atomic swap info with a non-existing swap id.
    Expect: atomic swap not found error message.
    """
    invalid_swap_id = '133102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3806'
    request_.params = {
        SWAP_ID: invalid_swap_id,
    }

    expected_error_message = f'Atomic swap with id "{invalid_swap_id}" not found.'

    mock_swap_get = mocker.patch('remme.clients.atomic_swap.AtomicSwapClient.swap_get')
    mock_swap_get.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await get_atomic_swap_info(request_)

    assert expected_error_message == error.value.message
