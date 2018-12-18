import os

KEY_DIR = '/etc/sawtooth/keys'
PRIV_KEY_FILE = os.path.join(KEY_DIR, 'validator.priv')
PUB_KEY_FILE = os.path.join(KEY_DIR, 'validator.pub')

SETTINGS_PUB_KEY_ENCRYPTION = 'remme.settings.pub_key_encryption'
SETTINGS_KEY_GENESIS_OWNERS = 'remme.settings.genesis_owners'
SETTINGS_SWAP_COMMISSION = 'remme.settings.swap_comission'
SETTINGS_STORAGE_PUB_KEY = 'remme.settings.storage_pub_key'

ZMQ_CONNECTION_TIMEOUT = 5

ZERO_ADDRESS = '0' * 70
GENESIS_ADDRESS = '0' * 69 + '1'
