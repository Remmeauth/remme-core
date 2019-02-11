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
import functools

from aiohttp_json_rpc import RpcInvalidParamsError


logger = logging.getLogger(__name__)


def validate_params(form_class, ignore_fields=None):
    def decorator(func):
        def _get_first_error(message):
            if isinstance(message, list):
                message = message[0]
                return _get_first_error(message)
            return message

        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            logger.debug(f'Req params: {request.params}')
            form = form_class(ignore_fields=ignore_fields, **request.params)
            if not form.validate():
                try:
                    message = _get_first_error(
                        list(form.errors.values())[0][0])
                except IndexError as e:
                    logger.exception(e)
                    message = 'Validation failed'
                raise RpcInvalidParamsError(message=message)

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


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
