import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.block_info import (
    fetch_block,
    get_blocks,
    list_blocks,
)
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)


@pytest.mark.asyncio
async def test_fetch_block(mocker, request_):
    """
    Case: fetch block by block id.
    Expect: particular block.
    """
    block_id = '92fa987b4f163b43d9f85641bb8ccf018022d3a9e2445e3c721e0b3cdfa83c42' \
               '65a21c74be9f6a732f75fcab1832637fa98816cd7fb43e42b9f609ffae1136fd'

    expected_result = {
        'data': {
            'batches': [
                {
                    'header': {
                        'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                        'transaction_ids': [
                            '29f640d436a5db153013c818d57702aee684954ee13d6ed6826a4645c9b25430'
                            '5d399de0e01a2456c5e51e09cd0889c11db9c4ee5f5096099e0ad2396c3e6441'
                        ]
                    },
                    'header_signature': '50898544a24cc09fbefb24402bcea4ff15801d6de0bb7d1b0af1402038f24e8e'
                                        '1f1bf25c782b1711c58547ee43573deb0f94656ade83ed8b70df41b7fcb4f2fe',
                    'trace': False,
                    'transactions': [
                        {
                            'header': {
                                'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb21'
                                                      '51403bd1582e8cd94a5153779c2107092',
                                'dependencies': [],
                                'family_name': 'block_info',
                                'family_version': '1.0',
                                'inputs': [
                                    '00b10c0100000000000000000000000000000000000000000000000000000000000000',
                                    '00b10c00'
                                ],
                                'nonce': '',
                                'outputs': [
                                    '00b10c0100000000000000000000000000000000000000000000000000000000000000',
                                    '00b10c00'
                                ],
                                'payload_sha512': '2dacbf1309ea8a9f24cc2b5ed1d99138922078731b5844f2bb80d00012c89698'
                                                  '3145fcac2d46af1552537af8b24648393130f1022a77d7bd43b650797ef01e3c',
                                'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb21'
                                                     '51403bd1582e8cd94a5153779c2107092'
                            },
                            'header_signature': '29f640d436a5db153013c818d57702aee684954ee13d6ed6826a4645c9b25430'
                                                '5d399de0e01a2456c5e51e09cd0889c11db9c4ee5f5096099e0ad2396c3e6441',
                            'payload': 'CtICCAESgAFhZGM0ZGY1NzdlNDM0ZjUzNjBkYTk2YTkzYjU0MDRmNjFiMzkyZDc2MjdhNjlhYzMy'
                                       'Y2U0YTYxODg5ZWE4NTEzMTk4Yzk2YTU4ODdlYTViYjM2NWU0ZjE1MzM3YjIzMWZhOWY2ZTRhMWNj'
                                       'ZTcwZDU3NTk4Yzg3YzRhYjVjNTQ0ZRpCMDJjMTcyZjlhMjc1MTJjMTFlMmQ0OWZkNDFhZGJjYjIx'
                                       'NTE0MDNiZDE1ODJlOGNkOTRhNTE1Mzc3OWMyMTA3MDkyIoABMzM3NDkyZDE5MDY3OGZiZTAxMWEy'
                                       'ZDA5MzcwNzdhYTk0OWQ1ODJlZWQ5Mzc4MWYzMmI0OTMyMDU1Zjc5MDEwNzNmODk3YTViNzA3ZWI4'
                                       'M2NkMTU1N2VmNGM3MGUzYzA5ZTEzNjhlZDlmODk3MTIwMWVlOGE0MDljYTQwN2UxNDMoos/o5AU='
                        }
                    ]
                },
            ],
            'header': {
                'batch_ids': [
                    '50898544a24cc09fbefb24402bcea4ff15801d6de0bb7d1b0af1402038f24e8e'
                    '1f1bf25c782b1711c58547ee43573deb0f94656ade83ed8b70df41b7fcb4f2fe',
                    'e7ce94ffd2ece31d69c123a9666158c4cdaca7522a41c87d6088364d309b8e2a'
                    '50f070e4b91b4f17796dc5248b344d69ed99bd4ee6aaa384a7d76a43a7256726'
                ],
                'block_num': '2',
                'consensus': 'RGV2bW9kZbBTi7/XqZI1BSUPdd+zjPl2xPTcd8WjLDB12DVIRWNV',
                'previous_block_id': '337492d190678fbe011a2d0937077aa949d582eed93781f32b4932055f790107'
                                     '3f897a5b707eb83cd1557ef4c70e3c09e1368ed9f8971201ee8a409ca407e143',
                'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                'state_root_hash': 'b865cf3ea5e5dc0698c37e464e65a5ac417fe5c643109c8c49d465d152dc027f'
            },
            'header_signature': '92fa987b4f163b43d9f85641bb8ccf018022d3a9e2445e3c721e0b3cdfa83c42'
                                '65a21c74be9f6a732f75fcab1832637fa98816cd7fb43e42b9f609ffae1136fd'
        }
    }

    mock_fetch_block = mocker.patch('remme.shared.router.Router.fetch_block')
    mock_fetch_block.return_value = return_async_value(expected_result)

    request_.params = {
        'id': block_id,
    }

    result = await fetch_block(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_block_id', ['12345', 0, 12345, True])
async def test_fetch_block_with_invalid_block_id(request_, invalid_block_id):
    """
    Case: fetch block with invalid block id.
    Expect: given block id is not a valid error message.
    """
    request_.params = {
        'id': invalid_block_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_block(request_)

    assert 'Given block id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('block_id_is_none', ['', None])
async def test_fetch_block_without_block_id(request_, block_id_is_none):
    """
    Case: fetch block without block id.
    Expect: missed id error message.
    """
    request_.params = {
        'id': block_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_block(request_)

    assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_block_with_non_existing_block_id(mocker, request_):
    """
    Case: fetch block with a non-existing block id.
    Expect: block with id not found error message.
    """
    invalid_block_id = '9d2dc2ab673d028bc1dd8b5be8d2d885e4383a827cd0261f58334252bf807c08' \
                       '113207eabbd12d0786d6bba5378a791129f9c520c17597b5504d4b547ef57491'
    request_.params = {
        'id': invalid_block_id,
    }

    expected_error_message = f'Block with id `{invalid_block_id}` not found.'

    mock_fetch_block = mocker.patch('remme.shared.router.Router.fetch_block')
    mock_fetch_block.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await fetch_block(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_fetch_block_with_wrong_key(request_):
    """
    Case: fetch block with wrong key.
    Expect: wrong params keys error message.
    """
    block_id = '92fa987b4f163b43d9f85641bb8ccf018022d3a9e2445e3c721e0b3cdfa83c42' \
               '65a21c74be9f6a732f75fcab1832637fa98816cd7fb43e42b9f609ffae1136fd'
    request_.params = {
        'address': block_id,
    }

    expected_error_message = "Wrong params keys: ['address']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_blocks(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('valid_params', [1, None])
async def test_get_blocks_with_valid_params(mocker, request_, valid_params):
    """
    Case: get blocks with parameter start.
    Expect: list of blocks.
    """
    request_.params = {
        'start': valid_params,
    }

    expected_result = [
        {
            'block_number': 1,
            'timestamp': 1553529639,
            'previous_header_signature': 0000000000000000,
            'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
            'header_signature': '0d355e7612d8bac6bc24a9d92d1b80c20c09aa0b155341774429386cdb2817a6'
                                '2d59694077f0df78b9b7222a500d267395900f06ee65a1198f76e3eb15949cdd'
        }
    ]

    mock_get_value = mocker.patch('remme.clients.block_info.BlockInfoClient.get_blocks_info')
    mock_get_value.return_value = return_async_value(expected_result)

    result = await get_blocks(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_params', ['12345', True])
async def test_get_blocks_with_invalid_params(request_, invalid_params):
    """
    Case: get blocks with invalid parameter start and limit.
    Expect: incorrect parameter identifier error message.
    """
    request_.params = {
        'start': invalid_params,
        'limit': invalid_params,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_blocks(request_)

    assert 'Incorrect parameter identifier.' == error.value.message


@pytest.mark.asyncio
async def test_get_blocks_with_non_exists_params_count(mocker, request_):
    """
    Case: get blocks with invalid parameter start.
    Expect: block not found error message.
    """
    request_.params = {
        'start': 123232456789098765456,
    }

    expected_error_message = 'Blocks not found.'

    mock_get_blocks_info = mocker.patch('remme.clients.block_info.BlockInfoClient.get_blocks_info')
    mock_get_blocks_info.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await get_blocks(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_get_blocks_with_wrong_key(request_):
    """
    Case: get blocks with wrong key.
    Expect: wrong params keys error message.
    """
    request_.params = {
        'address': '1',
    }

    expected_error_message = "Wrong params keys: ['address']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_blocks(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_list_blocks_with_wrong_key(request_):
    """
    Case: get list blocks with wrong key.
    Expect: wrong params keys error message.
    """
    request_.params = {
        'address': '11200759ba9b0d7ff93a3a8f6eb8e25fb5802d7caa8fad3d8bc19112b82f802a0cf9e7',
    }

    expected_error_message = "Wrong params keys: ['address']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_blocks(request_)

    assert expected_error_message == error.value.message
