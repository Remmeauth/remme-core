import logging

import remme
from remme.certificate.certificate_handler import CertificateHandler
from remme.token.token_handler import TokenHandler

REST_API_URL = 'http://rest-api:8080'
KEY_DIR = '/root/.sawtooth/keys'
PRIV_KEY_FILE = KEY_DIR + '/key.priv'
PUB_KEY_FILE = KEY_DIR + '/key.pub'
