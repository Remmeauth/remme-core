"""
Provide tests for atomic swap handler approving method implementation.
"""
import datetime
import time

import pytest
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg
from remme.protos.account_pb2 import Account
from remme.protos.atomic_swap_pb2 import (
    AtomicSwapApprovePayload,
    AtomicSwapInfo,
    AtomicSwapMethod,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512, web3_hash, client_to_real_amount
from remme.settings import TRANSACTION_FEE
from remme.tp.consensus_account import ConsensusAccountHandler, ConsensusAccount
from remme.tp.atomic_swap import AtomicSwapHandler
from remme.tp.basic import BasicHandler

TOKENS_AMOUNT_TO_SWAP = 200

BOT_ADDRESS = '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30'
BOT_PRIVATE_KEY = '1cb15ecfe1b3dc02df0003ac396037f85b98cf9f99b0beae000dc5e9e8b6dab4'
BOT_PUBLIC_KEY = '03ecc5cb4094eb05319be6c7a63ebf17133d4ffaea48cdcfd1d5fc79dac7db7b6b'

ALICE_ADDRESS = '112007db8a00c010402e2e3a7d03491323e761e0ea612481c518605648ceeb5ed454f7'

SECRET_KEY = '3e0b064c97247732a3b345ce7b2a835d928623cb2871c26db4c2539a38e61a16'
SECRET_LOCK = web3_hash(SECRET_KEY)

SWAP_ID = '033102e41346242476b15a3a7966eb5249271025fc7fb0b37ed3fdb4bcce3884'

ADDRESS_TO_STORE_SWAP_INFO_BY = BasicHandler(
    name=AtomicSwapHandler().family_name, versions=AtomicSwapHandler()._family_versions[0]
).make_address_from_data(data=SWAP_ID)


TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS = {
    'family_name': AtomicSwapHandler().family_name,
    'family_version': AtomicSwapHandler()._family_versions[0],
}

CURRENT_TIMESTAMP = int(datetime.datetime.now().timestamp())

RANDOM_NODE_PUBLIC_KEY = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

INPUTS = OUTPUTS = [
    ADDRESS_TO_STORE_SWAP_INFO_BY,
    BOT_ADDRESS,
    ConsensusAccountHandler.CONSENSUS_ADDRESS,
]


def test_approve_with_empty_proto():
    """
    Case: send empty proto for approve
    Expect: invalid transaction error
    """
    atomic_swap_init_payload = AtomicSwapApprovePayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_init_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert proto_error_msg(
        AtomicSwapApprovePayload,
        {
            'swap_id': ['Missed swap_id.'],
        }
    ) == str(error.value)


def test_approve_atomic_swap():
    """
    Case: approve atomic swap.
    Expect: atomic swap state is changed to approved.
    """
    atomic_swap_init_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_init_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    existing_swap_info = AtomicSwapInfo()
    existing_swap_info.swap_id = SWAP_ID
    existing_swap_info.state = AtomicSwapInfo.SECRET_LOCK_PROVIDED
    existing_swap_info.sender_address = BOT_ADDRESS
    existing_swap_info.secret_lock = SECRET_LOCK
    existing_swap_info.is_initiator = True
    serialized_existing_swap_info = existing_swap_info.SerializeToString()

    consensus_account = ConsensusAccount()
    consensus_account.block_cost = 0
    serialized_consensus_account = consensus_account.SerializeToString()

    sender_account = Account()
    sender_account.balance = client_to_real_amount(TRANSACTION_FEE)
    serialized_sender_account = sender_account.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_existing_swap_info,
        BOT_ADDRESS: serialized_sender_account,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_consensus_account,
    })

    expected_swap_info = AtomicSwapInfo()
    expected_swap_info.swap_id = SWAP_ID
    expected_swap_info.state = AtomicSwapInfo.APPROVED
    expected_swap_info.sender_address = BOT_ADDRESS
    expected_swap_info.secret_lock = SECRET_LOCK
    expected_swap_info.is_initiator = True
    serialized_expected_swap_info = expected_swap_info.SerializeToString()

    expected_consensus_account = ConsensusAccount()
    expected_consensus_account.block_cost = client_to_real_amount(TRANSACTION_FEE)
    serialized_expected_consensus_account = expected_consensus_account.SerializeToString()

    expected_sender_account = Account()
    expected_sender_account.balance = 0
    serialized_expected_sender_account = expected_sender_account.SerializeToString()

    expected_state = {
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_expected_swap_info,
        BOT_ADDRESS: serialized_expected_sender_account,
        ConsensusAccountHandler.CONSENSUS_ADDRESS: serialized_expected_consensus_account,
    }

    AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=[
        ADDRESS_TO_STORE_SWAP_INFO_BY,
        BOT_ADDRESS,
        ConsensusAccountHandler.CONSENSUS_ADDRESS,
    ])
    state_as_dict = {entry.address: entry.data for entry in state_as_list}

    assert expected_state == state_as_dict


def test_approve_not_initialized_atomic_swap():
    """
    Case: approve not initialized atomic swap.
    Expect: invalid transaction error is raised with atomic swap was not initiated error message.
    """
    atomic_swap_approve_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_approve_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={})

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Atomic swap was not initiated for identifier {SWAP_ID}!' == str(error.value)


def test_approve_already_closed_atomic_swap():
    """
    Case: to expire already closed atomic swap.
    Expect: invalid transaction error is raised with already operation with closed or expired swap error message.
    """
    atomic_swap_approve_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_approve_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    already_closed_swap_info = AtomicSwapInfo()
    already_closed_swap_info.swap_id = SWAP_ID
    already_closed_swap_info.state = AtomicSwapInfo.CLOSED
    serialized_already_closed_swap_info = already_closed_swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_already_closed_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'No operations can be done upon the swap: {SWAP_ID} as it is already closed or expired.' == str(error.value)


def test_approve_atomic_swap_by_bot():
    """
    Case: approve atomic swap by bot.
    Expect: invalid transaction error is raised with only transaction initiator may approve the swap error message.
    """
    atomic_swap_approve_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_approve_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    swap_info = AtomicSwapInfo()
    swap_info.swap_id = SWAP_ID
    swap_info.state = AtomicSwapInfo.OPENED
    swap_info.amount = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    swap_info.created_at = CURRENT_TIMESTAMP
    swap_info.sender_address = ALICE_ADDRESS
    swap_info.receiver_address = BOT_ADDRESS
    swap_info.is_initiator = True
    serialized_swap_info = swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Only transaction initiator (Alice) may approve the swap, once Bob provided a secret lock.' == \
           str(error.value)


def test_approve_atomic_swap_without_secret_lock():
    """
    Case: approve atomic swap without set secret lock.
    Expect: invalid transaction error is raised with only transaction initiator may approve the swap error message.
    """
    atomic_swap_approve_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_approve_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    swap_info = AtomicSwapInfo()
    swap_info.swap_id = SWAP_ID
    swap_info.state = AtomicSwapInfo.OPENED
    swap_info.amount = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    swap_info.created_at = CURRENT_TIMESTAMP
    swap_info.sender_address = BOT_ADDRESS
    swap_info.receiver_address = ALICE_ADDRESS
    swap_info.is_initiator = True
    serialized_swap_info = swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert 'Secret lock is needed for Bob to provide a secret key.' == str(error.value)


def test_approve_atomic_swap_without_secret_lock_state():
    """
    Case: approve atomic swap without secret lock state.
    Expect: invalid transaction error is raised with swap identifier is already closed error message.
    """
    atomic_swap_approve_payload = AtomicSwapApprovePayload(
        swap_id=SWAP_ID,
    )

    transaction_payload = TransactionPayload()
    transaction_payload.method = AtomicSwapMethod.APPROVE
    transaction_payload.data = atomic_swap_approve_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BOT_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=RANDOM_NODE_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BOT_PRIVATE_KEY).sign(serialized_header),
    )

    swap_info = AtomicSwapInfo()
    swap_info.swap_id = SWAP_ID
    swap_info.state = AtomicSwapInfo.OPENED
    swap_info.amount = client_to_real_amount(TOKENS_AMOUNT_TO_SWAP)
    swap_info.created_at = CURRENT_TIMESTAMP
    swap_info.sender_address = BOT_ADDRESS
    swap_info.secret_lock = SECRET_LOCK
    swap_info.receiver_address = ALICE_ADDRESS
    swap_info.is_initiator = True
    serialized_swap_info = swap_info.SerializeToString()

    mock_context = StubContext(inputs=INPUTS, outputs=OUTPUTS, initial_state={
        ADDRESS_TO_STORE_SWAP_INFO_BY: serialized_swap_info,
    })

    with pytest.raises(InvalidTransaction) as error:
        AtomicSwapHandler().apply(transaction=transaction_request, context=mock_context)

    assert f'Swap identifier {SWAP_ID} is already closed.' == str(error.value)
