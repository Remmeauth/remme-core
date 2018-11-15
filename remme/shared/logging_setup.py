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

import logging
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration
from sawtooth_sdk.processor.config import get_log_config

LOGGER = logging.getLogger(__name__)


def setup_logging(name, verbosity=2):
    log_config = get_log_config(filename='/etc/sawtooth/log_config.toml')

    if log_config is None:
        log_config = get_log_config(filename='/etc/sawtooth/log_config.yaml')

    if log_config is not None:
        try:
            log_configuration(log_config=log_config)
            LOGGER.info(f'Found and loaded logging configuration: {log_config}')
        except Exception as e:
            LOGGER.exception(e)
            LOGGER.info(f'Config has an error, skipping...')

    init_console_logging(verbose_level=verbosity)


def test(func):
    def wrapper(*args, **kwargs):
        LOGGER.info(f'Testing: {func.__name__} with args: {args}, '
                    f'kwargs: {kwargs}')
        return func(*args, **kwargs)
    return wrapper
