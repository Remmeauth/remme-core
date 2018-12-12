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
import logging
import importlib


logger = logging.getLogger(__name__)


def load_methods(prefix, modules="*"):
    if modules == '*':
        logger.info('Loading all modules')
        _smodules = []
        for i in os.listdir(os.path.dirname(__file__)):
            filename = os.path.splitext(i)[0]
            if not filename.startswith('__'):
                if os.path.splitext(i)[1] == '.py':
                    _smodules.append(filename)
        modules = ','.join(_smodules)

    logger.info(f'Got modules to load: {modules}')
    lmodules = map(lambda m: importlib.import_module(m, '*'),
                   (f'{prefix}.{module}' for module in modules.split(',')))
    for module in lmodules:
        _all = getattr(module, '__all__', [])
        logger.info(f'Found available methods in {module}: {_all}')
        for method in _all:
            try:
                yield getattr(module, method)
                logger.info(f'Method {method} loaded')
            except AttributeError:
                logger.info(f'Method {method} not found')
