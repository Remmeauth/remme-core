import os

KEY_DIR = '/etc/sawtooth/keys'
PRIV_KEY_FILE = os.path.join(KEY_DIR, 'validator.priv')
PUB_KEY_FILE = os.path.join(KEY_DIR, 'validator.pub')

SETTINGS_PUB_KEY_ENCRYPTION = 'remme.settings.pub_key_encryption'
SETTINGS_KEY_ZERO_ADDRESS_OWNERS = 'remme.settings.zero_address_owners'
SETTINGS_SWAP_COMMISSION = 'remme.settings.swap_comission'
SETTINGS_MINIMUM_STAKE = 'remme.settings.minimum_stake'
SETTINGS_GENESIS_OWNERS = 'remme.settings.genesis_owners'
SETTINGS_OBLIGATORY_PAYMENT = 'remme.settings.obligatory_payment'
SETTINGS_COMMITTEE_SIZE = 'remme.settings.committee_size'
CONSENSUS_ALLOWED_VALIDATORS = 'remme.consensus.allowed_validators'

ZMQ_CONNECTION_TIMEOUT = 30
# Number of seconds to wait for state operations to succeed
STATE_TIMEOUT_SEC = 30

ZERO_ADDRESS = '0' * 70
GENESIS_ADDRESS = '0' * 69 + '1'
NODE_STATE_ADDRESS = '0' * 69 + '2'
