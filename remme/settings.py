from remme.certificate.certificate_handler import CertificateHandler
from remme.token.token_handler import TokenHandler

REST_API_URL = 'http://rest-api:8008'
PRIV_KEY_FILE = '/root/.sawtooth/keys/key.priv'
PUB_KEY_FILE = '/root/.sawtooth/keys/key.pub'
TP_HANDLERS = [TokenHandler, CertificateHandler]