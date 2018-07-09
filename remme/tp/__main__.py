# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

import argparse

from sawtooth_sdk.processor.core import TransactionProcessor

from remme.tp.atomic_swap import AtomicSwapHandler
from remme.tp.pub_key import PubKeyHandler
from remme.tp.account import AccountHandler

from remme.shared.logging import setup_logging
from remme.settings import ENABLE_ECONOMY


TP_HANDLERS = [AccountHandler, PubKeyHandler, AtomicSwapHandler]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transaction processor.')
    parser.add_argument('endpoint')
    parser.add_argument('-v', '--verbosity', type=int, default=2)
    parser.add_argument('--account', action='store_true')
    parser.add_argument('--atomic-swap', action='store_true')
    parser.add_argument('--pubkey', action='store_true')
    args = parser.parse_args()
    setup_logging('remme', args.verbosity)

    processor = TransactionProcessor(url=args.endpoint)

    if args.account and ENABLE_ECONOMY:
        processor.add_handler(AccountHandler)
    if args.atomic_swap and ENABLE_ECONOMY:
        processor.add_handler(AtomicSwapHandler)
    if args.pubkey:
        processor.add_handler(PubKeyHandler)

    try:
        processor.start()
    except KeyboardInterrupt:
        pass
    finally:
        processor.stop()
