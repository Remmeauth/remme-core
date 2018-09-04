import os

import logging

LOGGER = logging.getLogger(__name__)

ZMQ_URL = 'tcp://127.0.0.1:4004'

KEY_DIR = '/root/.sawtooth/keys'
PRIV_KEY_FILE = KEY_DIR + '/key.priv'
PUB_KEY_FILE = KEY_DIR + '/key.pub'

SETTINGS_PUB_KEY_ENCRYPTION = 'remme.settings.pub_key_encryption'
SETTINGS_KEY_GENESIS_OWNERS = 'remme.settings.genesis_owners'
SETTINGS_SWAP_COMMISSION = 'remme.settings.swap_comission'

ZERO_ADDRESS = '0' * 70
GENESIS_ADDRESS = '0' * 69 + '1'
