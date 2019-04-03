import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.rpc_api.transaction import (
    get_batch_status,
    fetch_batch,
    list_batches,
    fetch_transaction,
    list_transactions,
)
from remme.shared.exceptions import KeyNotFound
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)


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
        'id': batch_id,
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
        'id': invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_batch_status(request_)

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('batch_id_is_none', ['', None])
async def test_get_batch_status_without_batch_id(request_, batch_id_is_none):
    """
    Case: get batch status without address.
    Expect: missed id error message.
    """
    request_.params = {
        'id': batch_id_is_none,
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
        'data': {
            'header': {
                'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                'transaction_ids': [
                    '5a7b019cf47e110a01295f173aebeae022c8249e9d5c4dab4c1681cf025fa405'
                    '1827fc1461a612839183698c4a8d6823bbfa11b85b99b801785e967657e18cd0'
                ]
            },
            'header_signature': '6907864c8ebc9bfc656c7f47716933786964e5b01f8844512df811379deb3d70'
                                '260ce126363fe79b6309c1ea1f556bdb34452b64136e5f5af7c31be3e0cccfd3',
            'trace': False,
            'transactions': [
                {
                    'header': {
                        'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                        'dependencies': [],
                        'family_name': 'account',
                        'family_version': '0.1',
                        'inputs': [
                            '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                            '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                        ],
                        'nonce': 'b66863cb325ad9471685de0d1e7240dd5a2cb17e0d0f144309190efc5d3cb6db'
                                 '5789cff4d493a8c631548f8d04e43810ef47cf1129a4df11f5f985817d61bdbb',
                        'outputs': [
                            '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                            '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                        ],
                        'payload_sha512': 'dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3'
                                          '0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990',
                        'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                    },
                    'header_signature': '5a7b019cf47e110a01295f173aebeae022c8249e9d5c4dab4c1681cf025fa405'
                                        '1827fc1461a612839183698c4a8d6823bbfa11b85b99b801785e967657e18cd0',
                    'payload': 'EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl'
                               'NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=='
                }
            ]
        }
    }

    mock_fetch_batch = mocker.patch('remme.shared.router.Router.fetch_batch')
    mock_fetch_batch.return_value = return_async_value(expected_result)

    request_.params = {
        'id': batch_id,
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
        'id': invalid_batch_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_batch(request_)

    assert 'Given batch id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('batch_id_is_none', ['', None])
async def test_fetch_batch_without_batch_id(request_, batch_id_is_none):
    """
    Case: fetch batch without batch id.
    Expect: missed id error message.
    """
    request_.params = {
        'id': batch_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_batch(request_)

    assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_batch_with_non_existing_batch_id(mocker, request_):
    """
    Case: fetch batch with a non-existing batch id.
    Expect: batch with batch id not found error message.
    """
    non_existing_batch_id = '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977' \
                            '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f1'
    request_.params = {
        'id': non_existing_batch_id,
    }

    expected_error_message = f'Batch with batch id `{non_existing_batch_id}` not found.'

    mock_fetch_batch = mocker.patch('remme.shared.router.Router.fetch_batch')
    mock_fetch_batch.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await fetch_batch(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('ids', [[1], ['123'], 123, True, 'e'])
async def test_list_batches_with_invalid_ids(request_, ids):
    """
    Case: list batches with invalid ids.
    Expect: exception with invalid id message is raised.
    """
    request_.params = {
        'ids': ids,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid id.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('start', [1, '1', True])
async def test_list_batches_with_invalid_start(request_, start):
    """
    Case: list batches with invalid start field.
    Expect: exception with invalid id message is raised.
    """
    request_.params = {
        'start': start,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid id.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [-1, '1', True])
async def test_list_batches_with_invalid_limit(request_, limit):
    """
    Case: list batches with invalid limit field.
    Expect: exception with invalid limit count message is raised.
    """
    request_.params = {
        'limit': limit,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid limit count.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('head', [1, '1', True])
async def test_list_batches_with_invalid_head(request_, head):
    """
    Case: list batches with invalid start field.
    Expect: exception with invalid id message is raised.
    """
    request_.params = {
        'head': head,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Invalid id.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('reverse', [1, '1', [1]])
async def test_list_batches_with_invalid_reverse(request_, reverse):
    """
    Case: list batches with invalid reverse field.
    Expect: exception invalid identifier message is raised.
    """
    request_.params = {
        'reverse': reverse
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_batches(request_)

    assert 'Incorrect identifier.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('start', ['a'*128])
async def test_list_batches_with_unexisting_start(request_, start):
    """
    Case: list batches with unexisting start.
    Expect: exception with resource not found message is raised.
    """
    request_.params = {
        'start': start,
    }

    with pytest.raises(KeyNotFound) as error:
        await list_batches(request_)

    assert 'Resource not found.' == error.value.message

@pytest.mark.asyncio
@pytest.mark.parametrize('ids', [['a'*128]])
async def test_list_batches_with_unexisting_ids(request_, ids):
    """
    Case: list batches with unexisting ids.
    Expect: exception with resource not found message is raised.
    """
    request_.params = {
        'ids': ids,
    }

    with pytest.raises(KeyNotFound) as error:
        await list_batches(request_)

    assert 'Resource not found.' == error.value.message

@pytest.mark.asyncio
async def test_list_batches_with_valid_params(mocker, request_,):
    """
    Case: list batches with valid params
    Expect: particular data.
    """
    start = '8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c' \
                     '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5'
    head = '8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c' \
                     '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5'
    ids = ['8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c' \
                     '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5']
    limit = 5

    expected_result = {
        'data': {
            'header': {
                'batcher_public_key': '02a65796f249091c3087614b4d9c292b00b8eba580d045ac2fd781224b87b6f13e',
                'family_name': 'sawtooth_settings',
                'family_version': '1.0',
                'inputs': [
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1c0cbf0fbcaf64c0b',
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c12840f169a04216b7',
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1918142591ba4e8a7',
                    '000000a87cb5eafdcca6a8f82af32160bc5311783bdad381ea57b4e3b0c44298fc1c14'
                ],
                'outputs': [
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1c0cbf0fbcaf64c0b',
                    '000000a87cb5eafdcca6a8f82af32160bc5311783bdad381ea57b4e3b0c44298fc1c14'
                ],
                'payload_sha512': '82dd686e5298d24826d68ec2cdfbd1438a1b1d37a88abeacd24e25386d5939fa'
                                  '139c3ab8b33ef594df804281c638887a0b9308c1f0a0922c5240202a4e2d0595',
                'signer_public_key': '02a65796f249091c3087614b4d9c292b00b8eba580d045ac2fd781224b87b6f13e',
                'dependencies': [],
                'nonce': ''
            },
            'header_signature': '8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c'
                                '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5',
            'payload': 'CAESRAoic2F3dG9vdGgudmFsaWRhdG9yLmJhdGNoX2luamVj'
                       'dG9ycxIKYmxvY2tfaW5mbxoSMHhhNGY2YzZhZWMxOWQ1OTBi'
        }
    }

    mock_fetch_transaction = mocker.patch('remme.shared.router.Router.list_batches')
    mock_fetch_transaction.return_value = return_async_value(expected_result)

    request_.params = {
        'start': start,
        'head': head,
        'limit': limit,
        'ids': ids,
    }

    result = await list_batches(request_)

    assert expected_result == result


@pytest.mark.asyncio
async def test_fetch_transaction(mocker, request_,):
    """
    Case: fetch transaction by id.
    Expect: particular transaction data.
    """
    transaction_id = '8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c' \
                     '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5'

    expected_result = {
        'data': {
            'header': {
                'batcher_public_key': '02a65796f249091c3087614b4d9c292b00b8eba580d045ac2fd781224b87b6f13e',
                'family_name': 'sawtooth_settings',
                'family_version': '1.0',
                'inputs': [
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1c0cbf0fbcaf64c0b',
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c12840f169a04216b7',
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1918142591ba4e8a7',
                    '000000a87cb5eafdcca6a8f82af32160bc5311783bdad381ea57b4e3b0c44298fc1c14'
                ],
                'outputs': [
                    '000000a87cb5eafdcca6a8cde0fb0dec1400c5ab274474a6aa82c1c0cbf0fbcaf64c0b',
                    '000000a87cb5eafdcca6a8f82af32160bc5311783bdad381ea57b4e3b0c44298fc1c14'
                ],
                'payload_sha512': '82dd686e5298d24826d68ec2cdfbd1438a1b1d37a88abeacd24e25386d5939fa'
                                  '139c3ab8b33ef594df804281c638887a0b9308c1f0a0922c5240202a4e2d0595',
                'signer_public_key': '02a65796f249091c3087614b4d9c292b00b8eba580d045ac2fd781224b87b6f13e',
                'dependencies': [],
                'nonce': ''
            },
            'header_signature': '8d8cb28c58f7785621b51d220b6a1d39fe5829266495d28eaf0362dc85d7e91c'
                                '205c1c4634604443dc566c56e1a4c0cf2eb122ac42cb482ef1436694634240c5',
            'payload': 'CAESRAoic2F3dG9vdGgudmFsaWRhdG9yLmJhdGNoX2luamVj'
                       'dG9ycxIKYmxvY2tfaW5mbxoSMHhhNGY2YzZhZWMxOWQ1OTBi'
        }
    }

    mock_fetch_transaction = mocker.patch('remme.shared.router.Router.fetch_transaction')
    mock_fetch_transaction.return_value = return_async_value(expected_result)

    request_.params = {
        'id': transaction_id,
    }

    result = await fetch_transaction(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_transaction_id', ['12345', 'Invalid id', 0, 12345, True])
async def test_fetch_transaction_with_invalid_id(request_, invalid_transaction_id):
    """
    Case: fetch transaction with invalid id.
    Expect: given transaction id is not a valid error message.
    """
    request_.params = {
        'id': invalid_transaction_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_transaction(request_)

    assert 'Given transaction id is not a valid.' == error.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize('transaction_id_is_none', ['', None])
async def test_fetch_transaction_without_id(request_, transaction_id_is_none):
    """
    Case: fetch transaction without id.
    Expect: missed id error message.
    """
    request_.params = {
        'id': transaction_id_is_none,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await fetch_transaction(request_)

    assert 'Missed id.' == error.value.message


@pytest.mark.asyncio
async def test_fetch_transaction_with_non_existing_id(mocker, request_):
    """
    Case: fetch transaction with a non-existing id.
    Expect: transaction not found error message.
    """
    non_existing_transaction_id = '5b3261a62694198d7eb034484abc06dfe997eca0f29f5f1019ba4d460e8b0977' \
                                  '3cf52f8235ab89c273da3725dd3c212c955734332777e02725e78333aba7f1f1'
    request_.params = {
        'id': non_existing_transaction_id,
    }

    expected_error_message = f'Transaction with id "{non_existing_transaction_id}" not found.'

    mock_fetch_transaction = mocker.patch('remme.shared.router.Router.fetch_transaction')
    mock_fetch_transaction.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await fetch_transaction(request_)

    assert expected_error_message == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_ids(mocker, request_):
    """
    Case: get list transactions by ids.
    Expect: list of transactions is fetched.
    """
    transaction_ids = ['d7da05756926c426bed6cd773f04d96c66be91efe2c973f8d19afb639791f05b'
                       '4f3641d0ec53bfa5f86a49d77acc7d0f463ce35d4b0c1a4cf0721d55c55b8150']

    expected_result = {
        'data': [
            {
                'header': {
                    'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                    'dependencies': [],
                    'family_name': 'account',
                    'family_version': '0.1',
                    'inputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'nonce': 'c4095bca57b47a919e9a8f8843edcff894511ae3013f9b6e0089d3af227e759a'
                             '21e4ff07ac0c91dbf3146aff1bd69d5f5f76357aca086dbaa13506e1d80ef555',
                    'outputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'payload_sha512': 'dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3'
                                      '0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990',
                    'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                },
                'header_signature': 'd7da05756926c426bed6cd773f04d96c66be91efe2c973f8d19afb639791f05b'
                                    '4f3641d0ec53bfa5f86a49d77acc7d0f463ce35d4b0c1a4cf0721d55c55b8150',
                'payload': 'EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl'
                           'NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=='
            }
        ],
        'head': '8d8480cb3f658a5289ce0661998d60e6f1ab813f16b76c09b55bb993e737442e'
                '5378713651e373c3e59a731755a35858b52f43ea1ec604bf37989c89df94e9bd',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_transactions = mocker.patch('remme.shared.router.Router.list_transactions')
    mock_list_transactions.return_value = return_async_value(expected_result)

    request_.params = {
        'ids': transaction_ids,
    }

    result = await list_transactions(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_ids', (['12345'], [0, ], ['12345', 12345], [True, False]))
async def test_list_transactions_with_invalid_ids(request_, invalid_ids):
    """
    Case: list transactions with invalid parameter ids.
    Expect: header signature is not of a blockchain token type error message.
    """
    request_.params = {
        'ids': invalid_ids,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert 'Header signature is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_start(mocker, request_):
    """
    Case: get list transactions by start.
    Expect: list of transactions is fetched.
    """
    expected_result = {
        'data': [
            {
                'header': {
                    'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                    'dependencies': [],
                    'family_name': 'account',
                    'family_version': '0.1',
                    'inputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'nonce': '3c44ae3266949a4d327000575f1e700ef7245251e487d068d62724802e440b4a'
                             'b4842ed56e70ba36b73b3360f3ea97c5fb9c90c62bc719f75397464afc44bed5',
                    'outputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'payload_sha512': 'dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3'
                                      '0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990',
                    'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                },
                'header_signature': '6a453ae6468bdaa77703bc05694312d9bc063e67aa17f32aabac72bdd74c71a7'
                                    '62781210f214444b7589eca166390f4f9b72d9c8704286982dd4e2fbe0917942',
                'payload': 'EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl'
                           'NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=='
            },
        ],
        'head': '39a3a13d6f78e427f65d52769b67d6aba8293a1dcc9b586c5f6ae01abf4d28bb'
                '45bdea660082f8210961826ba1b217cf251e0fe7529a1ad232e1fe5f369862e8',
        'paging': {
            'limit': None,
            'next': '',
            'start': '6a453ae6468bdaa77703bc05694312d9bc063e67aa17f32aabac72bdd74c71a7'
                     '62781210f214444b7589eca166390f4f9b72d9c8704286982dd4e2fbe0917942'
        }
    }

    mock_list_transactions = mocker.patch('remme.shared.router.Router.list_transactions')
    mock_list_transactions.return_value = return_async_value(expected_result)

    request_.params = {
        'start': '6a453ae6468bdaa77703bc05694312d9bc063e67aa17f32aabac72bdd74c71a7'
                 '62781210f214444b7589eca166390f4f9b72d9c8704286982dd4e2fbe0917942',
    }

    result = await list_transactions(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_start', ['12345', 0, 12345, True])
async def test_list_transactions_with_invalid_start(request_, invalid_start):
    """
    Case: list transactions with invalid parameter start.
    Expect: header signature is not of a blockchain token type error message.
    """
    request_.params = {
        'start': invalid_start,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert 'Header signature is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_limit(mocker, request_):
    """
    Case: get list transactions by limit.
    Expect: list of transactions is fetched.
    """
    expected_result = {
        'data': [
            {
                'header': {
                    'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
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
                    'payload_sha512': 'd364d81b082f81115b2b82f280dfed740b6715cd90e8ea20b74d5a1f2a9806d5'
                                      '897b3d7983ae2c35264121f9e2761c7a8f23d0e472751525975330fd56174fd0',
                    'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                },
                'header_signature': '8828a1cf43fbd09ae35617ab0451e5f21a95ebe7c4bde88548f5da77c965f03c'
                                    '716dc6daf57843ae68ef621854f489d72f0ed5e3ecb924170323ac33f6e70ac1',
                'payload': 'CtICCAESgAE5MGE5NGVjMjI2Y2NkZTM0YWJmMGZiZjBiMzk3NTNiOGYwZGRlMmJiN2Q3MTA4MjhmZDBhNjUxMTY0NT'
                           'JmYWIzMDA5ODA1YWI5ODMxN2NjYjY2OWExNzcwODE1YzA3ZjgyZjk4ZjU4MzlkMWVkMDNiYjZjY2M4NDFkZThhZmMx'
                           'NRpCMDJjMTcyZjlhMjc1MTJjMTFlMmQ0OWZkNDFhZGJjYjIxNTE0MDNiZDE1ODJlOGNkOTRhNTE1Mzc3OWMyMTA3MD'
                           'kyIoABYmY3MGRmYWQ1YjU1OTAxYjdiODFmNzZiNGE2N2I5MDA5M2VmNmM0YzBhOTcyY2YyOWMwN2YyZjU5NDQyNzBk'
                           'YzFlOWY3N2IyM2E0ODc0MzUyOGU3YzAyMDFiZGJhYjU5NWQ2M2IyZDMxOTM0YzcxYzcyYjUzMmJjNjgyZWQ2MDYoqa'
                           'qI5QU='
            }
        ],
        'head': '0de4bb8daee049d5b34368f4214cd5961b116ccecbba569ae21b0e06be0e6678'
                '09e7bb1d20e7616993e7b11e44cadff34fae59d0e545089bffbc3a7f23553cf7',
        'paging': {
            'limit': 1,
            'next': '2d7e063fea7a927a3241ff7987c1592ca9d4395a4d10b6bb073ed34d92060575'
                    '3482a901cdea9c38a3c9a48ecd2290f68bc4196c78d9ec8dbd7f849dcfa52161',
            'start': None
        }
    }

    mock_list_transactions = mocker.patch('remme.shared.router.Router.list_transactions')
    mock_list_transactions.return_value = return_async_value(expected_result)

    request_.params = {
        'limit': 1,
    }

    result = await list_transactions(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_limit', [True, '12345'])
async def test_list_transactions_with_invalid_limit(request_, invalid_limit):
    """
    Case: list transactions with invalid parameter limit.
    Expect: invalid limit count error message.
    """
    request_.params = {
        'limit': invalid_limit,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert 'Invalid limit count.' == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_head(mocker, request_):
    """
    Case: get list transactions by head.
    Expect: list of transactions is fetched.
    """
    expected_result = {
        'data': [
            {
                'header': {
                    'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                    'dependencies': [],
                    'family_name': 'account',
                    'family_version': '0.1',
                    'inputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'nonce': 'bb1f87a09e8d945cade322fa725503ca1b0f1af4755e65b663359bea31cece79'
                             'c835a18bcd0582bff3ca885afb660e4b9bd1413794b516b32f44a8d88eb20690',
                    'outputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'payload_sha512': 'dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3'
                                      '0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990',
                    'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                },
                'header_signature': '2d7e063fea7a927a3241ff7987c1592ca9d4395a4d10b6bb073ed34d92060575'
                                    '3482a901cdea9c38a3c9a48ecd2290f68bc4196c78d9ec8dbd7f849dcfa52161',
                'payload': 'EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl'
                           'NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=='
            }
        ],
        'head': '0de4bb8daee049d5b34368f4214cd5961b116ccecbba569ae21b0e06be0e6678'
                '09e7bb1d20e7616993e7b11e44cadff34fae59d0e545089bffbc3a7f23553cf7',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_transactions = mocker.patch('remme.shared.router.Router.list_transactions')
    mock_list_transactions.return_value = return_async_value(expected_result)

    request_.params = {
        'head': '0de4bb8daee049d5b34368f4214cd5961b116ccecbba569ae21b0e06be0e6678'
                '09e7bb1d20e7616993e7b11e44cadff34fae59d0e545089bffbc3a7f23553cf7',
    }

    result = await list_transactions(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_head', ['12345', 0, 12345, True])
async def test_list_transactions_with_invalid_head(request_, invalid_head):
    """
    Case: list transactions with invalid parameter head.
    Expect: given block id is not a valid error message.
    """
    request_.params = {
        'head': invalid_head,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert 'Given block id is not a valid.' == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_reverse(mocker, request_):
    """
    Case: get list transactions by reverse.
    Expect: list of transactions is fetched.
    """
    expected_result = {
        'data': [
            {
                'header': {
                    'batcher_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092',
                    'dependencies': [],
                    'family_name': 'account',
                    'family_version': '0.1',
                    'inputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'nonce': 'bb1f87a09e8d945cade322fa725503ca1b0f1af4755e65b663359bea31cece79'
                             'c835a18bcd0582bff3ca885afb660e4b9bd1413794b516b32f44a8d88eb20690',
                    'outputs': [
                        '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7',
                        '112007be95c8bb240396446ec359d0d7f04d257b72aeb4ab1ecfe50cf36e400a96ab9c'
                    ],
                    'payload_sha512': 'dfcee67257633b1e467054fcf179eedbf17aa013f565e637ff63c193631483b3'
                                      '0cedc741071accae4a564b8f6d241f7e322232d9acbb1dd4ecd2c94fc462f990',
                    'signer_public_key': '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
                },
                'header_signature': '2d7e063fea7a927a3241ff7987c1592ca9d4395a4d10b6bb073ed34d92060575'
                                    '3482a901cdea9c38a3c9a48ecd2290f68bc4196c78d9ec8dbd7f849dcfa52161',
                'payload': 'EkoSRjExMjAwN2RiOGEwMGMwMTA0MDJlMmUzYTdkMDM0OTEzMjNl'
                           'NzYxZTBlYTYxMjQ4MWM1MTg2MDU2NDhjZWViNWVkNDU0ZjcYCg=='
            }
        ],
        'head': '0de4bb8daee049d5b34368f4214cd5961b116ccecbba569ae21b0e06be0e6678'
                '09e7bb1d20e7616993e7b11e44cadff34fae59d0e545089bffbc3a7f23553cf7',
        'paging': {
            'limit': None,
            'next': '',
            'start': None
        }
    }

    mock_list_transactions = mocker.patch('remme.shared.router.Router.list_transactions')
    mock_list_transactions.return_value = return_async_value(expected_result)

    request_.params = {
        'reverse': 'false',
    }

    result = await list_transactions(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_reverse', ['12345', 0, 12345, True])
async def test_list_transactions_with_invalid_reverse(request_, invalid_reverse):
    """
    Case: list transactions with invalid parameter reverse.
    Expect: incorrect reverse identifier error message.
    """
    request_.params = {
        'reverse': invalid_reverse,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert 'Incorrect reverse identifier.' == error.value.message


@pytest.mark.asyncio
async def test_list_transactions_with_wrong_key(request_):
    """
    Case: list transactions with wrong key.
    Expect: wrong params keys error message.
    """
    request_.params = {
        'id': 'd7da05756926c426bed6cd773f04d96c66be91efe2c973f8d19afb639791f05b'
              '4f3641d0ec53bfa5f86a49d77acc7d0f463ce35d4b0c1a4cf0721d55c55b8150',
    }

    expected_error_message = "Wrong params keys: ['id']"

    with pytest.raises(RpcInvalidParamsError) as error:
        await list_transactions(request_)

    assert expected_error_message == error.value.message
