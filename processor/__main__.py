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

import os
import sys
import logging
import argparse
from sawtooth_sdk.processor.core import TransactionProcessor

sys.path.insert(0, os.getenv('PACKAGE_LOCATION', '/processor'))

from processor.certificate.certificate_handler import CertificateHandler
from processor.token.token_handler import TokenHandler

LOGGER = logging.getLogger(__name__)

# TODO: maybe add some logging
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transaction processor.')
    parser.add_argument('endpoint')
    args = parser.parse_args()
    LOGGER.info('Starting up')
    processor = TransactionProcessor(url=args.endpoint)
    processor.add_handler(TokenHandler())
    processor.add_handler(CertificateHandler())
    try:
        processor.start()
    except KeyboardInterrupt:
        pass
    finally:
        processor.stop()
