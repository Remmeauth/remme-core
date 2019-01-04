"""
Provide tests for atomic swap event handler implementation.
"""
import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.event._handlers import AtomicSwapEventHandler

BLOCK_ID = 'b2e08b7fd6e4568db5c3f8ed25a00f610ac9f3a1fec911c026cadccb3a5a1bd4' \
           '79da9f4e49b4eb9d28f17fefb925e64b447ab1c694e73a8871ab3120f09dd332'

VALID_SWAP_ID = '033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3884'

VALID_SWAP_ID_LENGTH = len(VALID_SWAP_ID)

atomic_swap_event_handler = AtomicSwapEventHandler()


def test_validate_atomic_swap_identifier():
    """
    Case: validate valid atomic swap identifier.
    Expect: identifier as dictionary with appropriate key is returned.
    """
    expected_result = {
        'id': VALID_SWAP_ID,
        'from_block': BLOCK_ID,
    }

    result = atomic_swap_event_handler.validate(msg_id=None, params={
        'id': VALID_SWAP_ID,
        'from_block': BLOCK_ID,
    })

    assert expected_result == result


@pytest.mark.parametrize(
    'invalid_atomic_swap_id',
    [
        pytest.param('3' * (VALID_SWAP_ID_LENGTH - 1), id='atomic swap identifier invalid length'),
        pytest.param('InvalidAtomicSwapIdentifier', id='text instead atomic swap identifier'),
        pytest.param('su' * (VALID_SWAP_ID_LENGTH // 2), id='not passed atomic swap identifier regexp'),
    ],
)
def test_validate_atomic_swap_invalid_identifier(invalid_atomic_swap_id):
    """
    Case: validate invalid atomic swap identifier.
    Expect: RPC invalid params error is raised with invalid params error message.
    """
    with pytest.raises(RpcInvalidParamsError) as error:
        atomic_swap_event_handler.validate(msg_id=None, params={
            'id': invalid_atomic_swap_id,
            'from_block': BLOCK_ID,
        })

    assert 'Invalid params' == str(error.value)
