import pytest


import time

from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction, TransactionHeader
)
from remme.tp.account import AccountHandler
from testing.mocks.stub import StubContext

from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest

from remme.protos.account_pb2 import Account

from remme.protos.account_pb2 import AccountMethod, TransferPayload
from remme.protos.transaction_pb2 import TransactionPayload

from remme.shared.utils import hash512

from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


def create_transaction_request(sender_params, address_to, amount, handler_params):
    """
    Create transaction request.

    Method `apply` of basic handler accepts transaction request that passed from validator.
    Validator accept not transaction request, but transaction, that have a bit another structure.

    Transaction -> RPC -> Validator -> (transaction request) Handler's apply

    See the difference by links:
        - https://sawtooth.hyperledger.org/docs/core/releases/1.0/_autogen/txn_submit_tutorial.html
        - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_token.py
        - https://github.com/Remmeauth/remme-client-python/blob/develop/remme/remme_transaction_service.py

    Some additional information besides references:
        - batcher public key - node you send transaction to public key;
        - consider payload as part of something that store some useful data;
        - inputs and outputs - lists with addresses transaction is related to. They are needed for the state
            (it is like a database under the hood of Sawtooth). For instance, if you transfer a 1000 tokens from
            first address to the second, state will change own records - in our case do subtraction for first address
            by 1000 token and addition the second one by the same 1000, then save it. Database can change data
            of addresses that are specified in outputs, but cannot in inputs (in inputs - only read data related to
            addresses).

    Arguments:
        sender_params (dict): sender's address, public and private keys.
        address_to (str): address to send tokens to.
        amount (int): amount of tokens to send.
        handler_params (dict): family name and version of handler that accepts transaction request.

    References:
        - https://github.com/Remmeauth/remme-core/blob/master/remme/tp/basic.py#L131
        - https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/architecture/transactions_and_batches.html
    """
    random_node_public_key = '039d6881f0a71d05659e1f40b443684b93c7b7c504ea23ea8949ef5216a2236940'

    transfer_payload = TransferPayload()
    transfer_payload.address_to = address_to
    transfer_payload.value = amount

    transaction_payload = TransactionPayload()
    transaction_payload.method = AccountMethod.TRANSFER
    transaction_payload.data = transfer_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=sender_params.get('public_key'),
        family_name=handler_params.get('family_name'),
        family_version=handler_params.get('family_version'),
        inputs=[sender_params.get('address'), address_to],
        outputs=[sender_params.get('address'), address_to],
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=random_node_public_key,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    private_key = Secp256k1PrivateKey.from_hex(sender_params.get('private_key'))
    signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=signer.sign(serialized_header),
    )

    return transaction_request
