import logging
import importlib


logger = logging.getLogger(__name__)


def load_methods(prefix, modules='*'):
    # TODO: Add * support
    logger.info(f'Got modules to load: {modules}')
    if modules == '*':
        raise NotImplementedError
    lmodules = map(lambda m: importlib.import_module(m, '*'),
                   (f'{prefix}.{module}' for module in modules.split(',')))
    for module in lmodules:
        _all = getattr(module, '__all__', [])
        logger.info(f'Found available methods in {module}: {_all}')
        for method in module.__all__:
            try:
                yield getattr(module, method)
                logger.info(f'Method {method} loaded')
            except AttributeError:
                logger.info(f'Method {method} not found in {module}')
