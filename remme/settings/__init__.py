import os

from remme.settings.default import load_toml_with_defaults

cfg_rest = load_toml_with_defaults('/config/remme-rest-api.toml')['remme']['rest_api']
cfg_ws = load_toml_with_defaults('/config/remme-client-config.toml')['remme']['client']
ZMQ_URL = f'tcp://{ cfg_ws["validator_ip"] }:{ cfg_ws["validator_port"] }'

KEY_DIR = '/etc/sawtooth/keys'
PRIV_KEY_FILE = os.path.join(KEY_DIR, 'validator.priv')
PUB_KEY_FILE = os.path.join(KEY_DIR, 'validator.pub')

SETTINGS_PUB_KEY_ENCRYPTION = 'remme.settings.pub_key_encryption'
SETTINGS_KEY_GENESIS_OWNERS = 'remme.settings.genesis_owners'
SETTINGS_SWAP_COMMISSION = 'remme.settings.swap_comission'

ZERO_ADDRESS = '0' * 70
GENESIS_ADDRESS = '0' * 69 + '1'
