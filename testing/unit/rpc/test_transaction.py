import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.transaction import (
    get_batch_status,
    fetch_batch,
)
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)

BATCH_ID = 'id'


@pytest.mark.asyncio
async def test_get_batch_status(mocker, request_,):
    """
    Case: get batch status by batch id.
    Expect: batch id status.
    """
    batch_id = '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977' \
               '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f5'
    list_statuses = {
        'data': [
            {
                'id': '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977'
                      '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f5',
                'status': 'COMMITTED',
                'invalid_transactions': [],
            },
        ],
    }

    mock_list_statuses = mocker.patch('remme.shared.router.Router.list_statuses')
    mock_list_statuses.return_value = return_async_value(list_statuses)

    request_.params = {
        BATCH_ID: batch_id,
    }

    result = await get_batch_status(request_)
    expected_result = 'COMMITTED'

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_batch_id', ['12345', 'Invalid id', 0, 12345, True])
async def test_get_batch_status_with_invalid_batch_id(request_, invalid_batch_id):
    """
    Case: get batch status with invalid batch id.
    Expect: given batch id is not a valid error message.
    """
    request_.params = {
        BATCH_ID: invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('batch_id_is_none', ['', None])
async def test_get_batch_status_without_batch_id(request_, batch_id_is_none):
    """
    Case: get batch status without address.
    Expect: missed ids error message.
    """
    request_.params = {
        BATCH_ID: batch_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_batch(mocker, request_,):
    """
    Case: fetch batch by batch id.
    Expect: particular batch data.
    """
    batch_id = '6907864c8ebc9bfc656c7f47716933786964e5b01f8844512df811379deb3d70' \
               '260ce126363fe79b6309c1ea1f556bdb34452b64136e5f5af7c31be3e0cccfd3'

    expected_result = {
        "data": {
            "header": {
                "signer_public_key": "02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092",
                "transaction_ids": [
                    "5a7b019cf47e110a01295f173aebeae022c8249e9d5c4dab4c1681cf025fa405"
                    "1827fc1461a612839183698c4a8d6823bbfa11b85b99b801785e967657e18cd0"
                ]
            },
            "header_signature": "6907864c8ebc9bfc656c7f47716933786964e5b01f8844512df811379deb3d70"
                                "260ce126363fe79b6309c1ea1f556bdb34452b64136e5f5af7c31be3e0cccfd3",
            "trace": False,
            "transactions": [
                {
                    "header": {
                        "batcher_public_key": "02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092",
                        "dependencies": [],
                        "family_name": "account",
                        "family_version": "0.1",
                        "inputs": [
                            "112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7",
                            "112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c"
                        ],
                        "nonce": "b66863cb325ad9471685de0d1e7240dd5a2cb17e0d0f144309190efc5d3cb6db"
                                 "5789cff4d493a8c631548f8d04e43810ef47cf1129a4df11f5f985817d61bdbb",
                        "outputs": [
                            "112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7",
                            "112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c"
                        ],
                        "payload_sha512": "dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3"
                                          "0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990",
                        "signer_public_key": "02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092"
                    },
                    "header_signature": "5a7b019cf47e110a01295f173aebeae022c8249e9d5c4dab4c1681cf025fa405"
                                        "1827fc1461a612839183698c4a8d6823bbfa11b85b99b801785e967657e18cd0",
                    "payload": "EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl"
                               "NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=="
                }
            ]
        }
    }

    mock_fetch_batch = mocker.patch('remme.shared.router.Router.fetch_batch')
    mock_fetch_batch.return_value = return_async_value(expected_result)

    request_.params = {
        BATCH_ID: batch_id,
    }

    result = await fetch_batch(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_batch_id', ['12345', 'Invalid id', 0, 12345, True])
async def test_fetch_batch_with_invalid_batch_id(request_, invalid_batch_id):
    """
    Case: fetch batch with invalid batch id.
    Expect: given batch id is not a valid error message.
    """
    request_.params = {
        BATCH_ID: invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_batch(request_)

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('batch_id_is_none', ['', None])
async def test_fetch_batch_without_batch_id(request_, batch_id_is_none):
    """
    Case: fetch batch without batch id.
    Expect: missed ids error message.
    """
    request_.params = {
        BATCH_ID: batch_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_batch(request_)

    assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_batch_with_non_existing_batch_id(mocker, request_):
    """
    Case: fetch batch with a non-existing batch id.
    Expect: batch not found error message.
    """
    invalid_batch_id = '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977' \
                       '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f1'
    request_.params = {
        BATCH_ID: invalid_batch_id,
    }

    expected_error_message = f'Batch with batch id `{invalid_batch_id}` not found.'

    mock_fetch_batch = mocker.patch('remme.shared.router.Router.fetch_batch')
    mock_fetch_batch.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await fetch_batch(request_)

    assert expected_error_message == error.value.message
