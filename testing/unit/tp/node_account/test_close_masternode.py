"""
Provide tests for node account handler apply (genesis) method implementation.
"""
import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.account_pb2 import (
    Account,
    AccountMethod,
    TransferPayload,
)
from remme.protos.node_account_pb2 import NodeAccountInternalTransferPayload, NodeAccountMethod, NodeAccount
from remme.protos.transaction_pb2 import TransactionPayload
from remme.settings import ZERO_ADDRESS
from remme.shared.utils import hash512
from remme.tp.account import AccountHandler
from remme.tp.node_account import NodeAccountHandler
from testing.conftest import create_signer
from testing.mocks.stub import StubContext
from testing.utils.client import proto_error_msg

from .shared import *


