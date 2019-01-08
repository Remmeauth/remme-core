"""
Provide tests for transfer event handler implementation.
"""
import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.event._handlers import TransferEventHandler

VALID_ADDRESS = '112007' + 'db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'

VALID_ADDRESS_LENGTH = len(VALID_ADDRESS)

transfer_event_handler = TransferEventHandler()


def test_validate_transfer_address():
    """
    Case: validate transfer address.
    Expect: address as dictionary with appropriate key is returned.
    """
    expected_result = {
        'address': VALID_ADDRESS,
    }

    result = transfer_event_handler.validate(msg_id=None, params={
        'address': VALID_ADDRESS,
    })

    assert expected_result == result


def test_validate_transfer_address_no_address():
    """
    Case: validate not specified transfer address.
    Expect: RPC invalid params error is raised with invalid params error message.
    """
    with pytest.raises(RpcInvalidParamsError) as error:
        transfer_event_handler.validate(msg_id=None, params={})

    assert 'Invalid params' == str(error.value)


@pytest.mark.parametrize(
    'invalid_transfer_address',
    [
        pytest.param('112007' + 'db8a00c010402e', id='transfer address invalid length'),
        pytest.param('InvalidTransferAddress', id='text instead transfer address'),
        pytest.param('su' * (VALID_ADDRESS_LENGTH // 2), id='not passed transfer address regexp'),
    ],
)
def test_validate_invalid_id(invalid_transfer_address):
    """
    Case: validate invalid transfer address.
    Expect: RPC invalid params error is raised with invalid params error message.
    """
    with pytest.raises(RpcInvalidParamsError) as error:
        transfer_event_handler.validate(msg_id=None, params={
            'address': invalid_transfer_address,
        })

    assert 'Invalid params' == str(error.value)
