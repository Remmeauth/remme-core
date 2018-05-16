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
from pathlib import Path
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.config import get_log_dir

LOGGER = logging.getLogger(__name__)

def setup_logging(name, verbosity=2):
    Path('/var/log/sawtooth').mkdir(parents=True, exist_ok=True)
    Path('/var/log/sawtooth/{}-debug.log'.format(name)).touch(exist_ok=True)

    log_config = get_log_config(filename='{}_log_config.toml'.format(name))

    if log_config is None:
        log_config = get_log_config(filename='{}_log_config.yaml'.format(name))

    if log_config is not None:
        log_configuration(log_config=log_config)
    else:
        log_dir = get_log_dir()
        log_configuration(log_dir=log_dir, name=name)

    init_console_logging(verbose_level=verbosity)


def test(func):
    def wrapper(*args, **kwargs):
        LOGGER.info('Testing: {} with args: {}, kwargs: {}'.format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper

