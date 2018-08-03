#!/bin/python3

import toml

if __name__ == '__main__':
    config = toml.load('/config/remme-genesis-config.toml')['remme']['genesis']
    print('export REMME_CONSENSUS={};'.format(config['consensus']))
    print('export REMME_ECONOMY_ENABLED={};'.format(config['economy_enabled']))
