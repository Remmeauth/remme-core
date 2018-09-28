#!/bin/python3

import toml


def _merge_deep(a, b):
    common = list(set(a.keys()) & set(b.keys()))
    merged = {**a, **b}
    for key in common:
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            merged[key] = _merge_deep(a[key], b[key])
    return merged


def load_toml_with_defaults(filename, subpath=None, defaults=None):
    value = toml.load(filename)
    if isinstance(subpath, list):
        for key in subpath:
            value = value[key]
    if isinstance(defaults, dict):
        value = _merge_deep(defaults, value)
    return value

DEFAULT_GENESIS_CONFIG = {
    'token_supply': 1000000000000,
    'economy_enabled': True,
    'consensus': 'poet-simulator',
}

if __name__ == '__main__':
    config = load_toml_with_defaults('/config/remme-genesis-config.toml', ['remme', 'genesis'], DEFAULT_GENESIS_CONFIG)
    print('export REMME_CONSENSUS={};'.format(config['consensus']))
    print('export REMME_ECONOMY_ENABLED={};'.format(config['economy_enabled']))
