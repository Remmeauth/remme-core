import logging

from remme.tp.pub_key import PUB_KEY_STORE_PRICE, PUB_KEY_ORGANIZATION, PUB_KEY_MAX_VALIDITY

from remme.clients.account import AccountClient
from remme.tp.account import AccountHandler

from remme.shared.exceptions import KeyNotFound

from remme.clients.pub_key import PubKeyClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime


from OpenSSL import crypto


LOGGER = logging.getLogger(__name__)


def pub_key_put_request(func):
    def validation_logic(payload):
        cert, key, key_export = create_certificate(payload)
        if not is_valid_token_balance():
            return {'error': 'You have no tokens to issue pub_key'}, 402
        if pub_key_already_exist(cert):
            return {'error': 'This pub_key is already registered'}, 409
        if cert.not_valid_after - cert.not_valid_before > PUB_KEY_MAX_VALIDITY:
            return {'error': 'The pub_key validity exceeds the maximum value'}, 400

        name_to_save = payload['name_to_save'] if 'name_to_save' in payload else None
        passphrase = payload['passphrase'] if 'passphrase' in payload else None

        return func(cert, key, key_export, name_to_save, passphrase)

    return validation_logic


def pub_key_address_request(func):
    def validation_logic(payload):
        try:
            serialization.load_pem_public_key(payload['pub_key'].encode('utf-8'),
                                              default_backend())
            address = PubKeyClient().make_address_from_data(payload['pub_key'])
            LOGGER.debug(f'fetch pub_key_address {address}')
        except ValueError:
            return {'error': 'Unable to load pub_key entity'}, 422
        return func(address)

    return validation_logic


def cert_key_address_request(func):
    def validation_logic(payload):
        try:
            certificate = x509.load_pem_x509_certificate(payload['crt_key'].encode('utf-8'),
                                                         default_backend())
            pub_key = certificate.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                            format=serialization.PublicFormat.SubjectPublicKeyInfo)
            address = PubKeyClient().make_address_from_data(pub_key)
            LOGGER.debug(f'fetch crt_key_address {address}')
        except ValueError:
            return {'error': 'Unable to load crt_key entity'}, 422
        return func(address)

    return validation_logic


def p12_pub_key_address_request(func):
    def validation_logic(pub_key, passphrase=''):
        try:
            p12 = crypto.load_pkcs12(pub_key.read(), passphrase)
            pub_cert = p12.get_certificate().to_cryptography()
            pub_key = pub_cert.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                         format=serialization.PublicFormat.SubjectPublicKeyInfo)
            address = PubKeyClient().make_address_from_data(pub_key)
        except ValueError:
            return {'error': 'Unable to load pub_key entity'}, 422
        except crypto.Error:
            return {'error': 'Incorrect passphrase'}, 403

        return func(address)

    return validation_logic


def pub_key_sign_request(func):
    def validation_logic(payload):
        try:
            pub_key = x509.load_pem_x509_csr(payload['pub_key'].encode('utf-8'),
                                             default_backend())
            if not is_valid_token_balance():
                return {'error': 'You have no tokens to issue pub_key'}, 402

            not_valid_before = payload.get('not_valid_before', None)
            not_valid_after = payload.get('not_valid_after', None)

            not_valid_before = datetime.datetime.fromtimestamp(not_valid_before) if not_valid_before else datetime.datetime.utcnow()
            not_valid_after = datetime.datetime.fromtimestamp(not_valid_after) if not_valid_after else not_valid_before + PUB_KEY_MAX_VALIDITY

            if not_valid_after:
                if not_valid_before >= not_valid_after:
                    return {'error': 'not_valid_before pub_key property has to occur before the not_valid_after'}, 400
                if not_valid_after - not_valid_before > PUB_KEY_MAX_VALIDITY:
                    return {'error': 'The pub_key validity exceeds the maximum value.'}, 400

        except ValueError:
            return {'error': 'Unable to load pub_key request entity'}, 422

        return func(pub_key, not_valid_before, not_valid_after)

    return validation_logic


# hot fix - as far as connexion has a bug inside it is
# temp solution for null body cases
# https://github.com/zalando/connexion/issues/579
def http_payload_required(func):
    def func_wrapper(payload):
        if payload is None:
            return {'error': 'Http request body can not be empty'}, 422

        return func(payload)

    return func_wrapper


def create_certificate(payload, org_name=PUB_KEY_ORGANIZATION, signer=None):
    parameters = get_params()
    encryption_algorithm = get_encryption_algorithm(payload)

    key = generate_key()
    key_export = generate_key_export(key, encryption_algorithm)

    if not signer:
        signer = PubKeyClient().get_signer()
    cert = build_certificate(parameters, payload, key, signer.get_public_key().as_hex(), org_name)

    return cert, key, key_export


def build_certificate(parameters, payload, key, signer_pub_key, org_name):
    name_oid = [x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
                x509.NameAttribute(NameOID.USER_ID, signer_pub_key)]

    for k, v in parameters.items():
        if k in payload.keys():
            name_oid.append(x509.NameAttribute(v, payload[k]))

    subject = issuer = x509.Name(name_oid)

    not_valid_before, not_valid_after = get_dates_from_payload(payload)

    return x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        not_valid_before
    ).not_valid_after(
        not_valid_after
    ).sign(key, hashes.SHA256(), default_backend())


def get_dates_from_payload(payload):
    if 'validity_after' in payload:
        not_valid_before = datetime.datetime.utcnow() + datetime.timedelta(days=payload['validity_after'])
    else:
        not_valid_before = datetime.datetime.utcnow()

    if 'validity' in payload:
        not_valid_after = not_valid_before + datetime.timedelta(days=payload['validity'])
    else:
        not_valid_after = not_valid_before + PUB_KEY_MAX_VALIDITY

    return not_valid_before, not_valid_after


def get_params():
    return {
        'country_name': NameOID.COUNTRY_NAME,
        'state_name': NameOID.STATE_OR_PROVINCE_NAME,
        'street_address': NameOID.STREET_ADDRESS,
        'postal_address': NameOID.POSTAL_ADDRESS,
        'postal_code': NameOID.POSTAL_CODE,
        'locality_name': NameOID.LOCALITY_NAME,
        'common_name': NameOID.COMMON_NAME,
        'name': NameOID.GIVEN_NAME,
        'surname': NameOID.SURNAME,
        'pseudonym': NameOID.PSEUDONYM,
        'business_category': NameOID.BUSINESS_CATEGORY,
        'title': NameOID.TITLE,
        'email': NameOID.EMAIL_ADDRESS,
        'serial': NameOID.SERIAL_NUMBER,
        'generation_qualifier': NameOID.GENERATION_QUALIFIER
    }


def get_encryption_algorithm(payload):
    encryption_algorithm = serialization.NoEncryption()
    if 'passphrase' in payload.keys():
        if payload['passphrase']:
            encryption_algorithm = serialization.BestAvailableEncryption(
                payload['passphrase'].encode('utf-8'))
    return encryption_algorithm


def generate_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )


def generate_key_export(key, encryption_algorithm):
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption_algorithm
    )


def is_valid_token_balance():
    account_client = AccountClient()
    signer_pub_key = account_client.get_signer().get_public_key().as_hex()
    signer_balance = account_client.get_balance(AccountHandler.make_address_from_data(signer_pub_key))
    return signer_balance >= PUB_KEY_STORE_PRICE


def pub_key_already_exist(cert):
    account_client = AccountClient()
    address = account_client.make_address_from_data(cert.public_bytes(serialization.Encoding.DER).hex())
    try:
        account_client.get_value(address)
    except KeyNotFound:
        return False
    return True
