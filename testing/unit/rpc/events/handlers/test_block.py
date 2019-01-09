"""
Provide tests for block event handler implementation.
"""
import pytest

from remme.rpc_api.event._handlers import BlockEventHandler
from remme.protos.block_info_pb2 import BlockInfo

from testing.utils.async_ import return_async_value

BLOCK_ID = '5cae0c8f4b67f7dc91d2b06a583d8d49ac126be221b9a34f661094cb4c12db94' \
           '011ecda7d0754f271bf48b63f9501da2a78a4bf67be8634f3ed9c43badafbc4b'


block_event_handler = BlockEventHandler()


@pytest.mark.asyncio
async def test_prepare_response(mocker):
    """
    Case: prepare response.
    Expect: timestamp along with block identifier is returned.
    """
    block_info = BlockInfo()
    block_info.block_num = 5
    block_info.timestamp = 1546962851
    serialized_block_info = block_info.SerializeToString()

    mock_get_block_value = mocker.patch('remme.clients.basic.BasicClient.get_value')
    mock_get_block_value.return_value = return_async_value(serialized_block_info)

    expected_result = {
        'id': BLOCK_ID,
        'timestamp': 1546962851,
    }

    result = await block_event_handler.prepare_response(state={
        'block_id': BLOCK_ID,
        'block_num': 5,
    }, validated_data=None)

    assert expected_result == result


def test_parse_event_attributes():
    """
    Case: prepare event attributes.
    Expect: attributes converted from array of dictionary to whole dictionary.
    """
    expected_result = {
        'block_id': BLOCK_ID,
        'block_num': 5,
    }

    result = block_event_handler.parse_evt(evt={
        'attributes': [
            {'key': None, 'value': None},
            {'key': 'block_id', 'value': BLOCK_ID},
            {'key': 'block_num', 'value': 5},
        ]
    })

    assert expected_result == result
