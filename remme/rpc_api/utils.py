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
