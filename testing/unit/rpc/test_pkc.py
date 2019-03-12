import pytest
from aiohttp_json_rpc.exceptions import RpcInvalidParamsError

from remme.protos.pub_key_pb2 import (
    NewPubKeyPayload,
    PubKeyStorage,
)
from remme.rpc_api.pkc import get_public_key_info
from remme.shared.exceptions import KeyNotFound
from testing.unit.tp.public_key.base import (
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP_PLUS_YEAR,
)
from testing.utils._async import (
    raise_async_error,
    return_async_value,
)

PUBLIC_KEY_ADDRESS = 'public_key_address'

ENTITY_HASH = '3409ab9912c4bbb900648f327f62a5d8a45ff5dc52f437aad44b75b5c4f7a95b' \
              'cac6b7163ffbaa22bbf87dcb77805940e80fab785d95685e68b4f9e8f559a7ea'

ENTITY_HASH_SIGNATURE = 'a14a34a8833b6beec718393849baadd687243caa684b0a7ab52af1a7594708d43a38e837d47e429465fcc' \
                        '2ebcb509fd30334fd6b76ca87cce48ebdc44aa8081ba95616602c209dab25ec89780d8f787e4efcc33b04' \
                        '4149d40ed52aeeba3dd9ec4f41ad915ab55f4acfbad9c9a5dd85388c2e5adf8627ea13a1834dc76a17699' \
                        '7a952ed37c4c481504970e1c271ae525abd894d4a87a983101f5a2d1ed6e8d66b809ba562ae0b82df19af' \
                        '60d88cb0604aa3531349b7a560b57fe9f667f470bae111e1b3c37d48382360a0d2ff0664950460d24b562' \
                        '90b688623d2db6eccc2a9050aca3c6aa16e5c578bacfb7c881be9d2583a5599a41eb387c691dfb6bf6d6c0f'

PUBLIC_KEY = '30820122300d06092a864886f70d01010105000382010f003082010a0282010100c5e8b5c4bf88580520629442b33cb6' \
             '0b6cdbfb620ad7a39afa0931ba9b9b988bc0fb0f4083338985f8153980ef778df9b557dc5d728d13d57010d3d6520d7c' \
             '769abe24c9db25b7045561a95a77f347a8bb64d29c547cb3dc6d2469578a7f33be244bfa664083c5fd0f31216aeb3ff9' \
             'fb740550db42916290f13856a18009c9631c20b8ece52f7264b740445b0f7b1497115f14fdffafc0c2c370cf3dbb8d90' \
             '26731acddcf8b6d2bf8648ff6c5fa21a6ff258fcd4b127d7b014c84c7f692b5a9713eb8f4bb8bbab04cb78aa58f13088' \
             '8c839febd7b2a92faffed1118c855f9cf78318af1990972a8c1a5ca912b52003c94d5504e43aec7813a8b664e3e9aced' \
             'a90203010001'


@pytest.mark.asyncio
async def test_get_public_key_info(mocker, request_):
    """
    Case: get public key information.
    Expect: information about public key in json format.
    """
    new_pub_key_payload = NewPubKeyPayload(
        entity_hash=ENTITY_HASH.encode('utf-8'),
        entity_hash_signature=bytes.fromhex(ENTITY_HASH_SIGNATURE),
        valid_from=int(CURRENT_TIMESTAMP),
        valid_to=int(CURRENT_TIMESTAMP_PLUS_YEAR),
        rsa=NewPubKeyPayload.RSAConfiguration(
            padding=NewPubKeyPayload.RSAConfiguration.Padding.Value('PSS'),
            key=bytes.fromhex(PUBLIC_KEY),
        ),
        hashing_algorithm=NewPubKeyPayload.HashingAlgorithm.Value('SHA256'),
    )

    pub_key_storage = PubKeyStorage()
    pub_key_storage.owner = '02c172f9a27512c11e2d49fd41adbcb2151403bd1582e8cd94a5153779c2107092'
    pub_key_storage.is_revoked = False
    pub_key_storage.payload.MergeFrom(new_pub_key_payload)

    serialize = pub_key_storage.SerializeToString()

    mock_get_value = mocker.patch('remme.clients.basic.BasicClient.get_value')
    mock_get_value.return_value = return_async_value(serialize)

    public_key_address = 'a23be1d1b2a99bbe819b4dbfad693eabda84137bb99138da8b8f8c0d578ce8dc8f7ef9'

    request_.params = {
        PUBLIC_KEY_ADDRESS: public_key_address,
    }

    expected_result = {
        'is_revoked': False,
        'owner_public_key': str(pub_key_storage.owner),
        'type': 'rsa',
        'is_valid': True,
        'valid_from': int(CURRENT_TIMESTAMP),
        'valid_to': int(CURRENT_TIMESTAMP_PLUS_YEAR),
        'public_key': PUBLIC_KEY,
        'entity_hash': ENTITY_HASH,
        'entity_hash_signature': ENTITY_HASH_SIGNATURE,
    }

    result = await get_public_key_info(request_)

    assert expected_result == result


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid_swap_id', ['12345', 12345, True])
async def test_get_public_key_info_with_invalid_public_key_address(request_, invalid_swap_id):
    """
    Case: get public key info with invalid public key address.
    Expect: address is not of a blockchain token type error message.
    """
    request_.params = {
        PUBLIC_KEY_ADDRESS: invalid_swap_id,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_public_key_info(request_)

    assert 'Address is not of a blockchain token type.' == error.value.message


@pytest.mark.asyncio
async def test_get_public_key_info_without_public_key_address(request_):
    """
    Case: get public key info without public key address.
    Expect: missed address error message.
    """
    request_.params = {
        PUBLIC_KEY_ADDRESS: None,
    }

    with pytest.raises(RpcInvalidParamsError) as error:
        await get_public_key_info(request_)

    assert 'Missed address.' == error.value.message


@pytest.mark.asyncio
async def test_get_atomic_swap_with_non_existing_public_key_address(mocker, request_):
    """
    Case: get public key info with a non-existing public key address.
    Expect: public key info not found error message.
    """
    invalid_public_key_address = 'a23be1ca4f8631a860451537aad71d1fcf2e5ec62854b5f8838c20d4b6990b0a1c9cdc'
    request_.params = {
        PUBLIC_KEY_ADDRESS: invalid_public_key_address,
    }

    expected_error_message = 'Public key info not found'

    mock_swap_get = mocker.patch('remme.clients.pub_key.PubKeyClient.get_status')
    mock_swap_get.return_value = raise_async_error(KeyNotFound(expected_error_message))

    with pytest.raises(KeyNotFound) as error:
        await get_public_key_info(request_)

    assert expected_error_message == error.value.message
