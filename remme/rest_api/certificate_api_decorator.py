from remme.certificate.handler import CERT_STORE_PRICE, CERT_ORGANIZATION, CERT_MAX_VALIDITY

from remme.account.client import AccountClient
from remme.account.handler import AccountHandler

from remme.shared.exceptions import KeyNotFound

from remme.certificate.client import CertificateClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import datetime


from OpenSSL import crypto
from OpenSSL.crypto import PKCS12, X509, PKey


def certificate_put_request(func):
    def validation_logic(payload):
        cert, key, key_export = create_certificate(payload)
        if not is_valid_token_balance():
            return {'error': 'You have no tokens to issue certificate'}, 402
        if certificate_already_exist(cert):
            return {'error': 'This certificate is already registered'}, 409
        if cert.not_valid_after - cert.not_valid_before > CERT_MAX_VALIDITY:
            return {'error': 'The certificate validity exceeds the maximum value'}, 400

        name_to_save = payload['name_to_save'] if 'name_to_save' in payload else None
        passphrase = payload['passphrase'] if 'passphrase' in payload else None

        return func(cert, key, key_export, name_to_save, passphrase)

    return validation_logic


def certificate_address_request(func):
    def validation_logic(payload):
        try:
            certificate = x509.load_pem_x509_certificate(payload['certificate'].encode('utf-8'),
                                                         default_backend())
            crt_bin = certificate.public_bytes(serialization.Encoding.DER).hex()
            address = CertificateClient().make_address_from_data(crt_bin)
        except ValueError:
            return {'error': 'Unable to load certificate entity'}, 422

        return func(address)

    return validation_logic


def p12_certificate_address_request(func):
    def validation_logic(certificate, passphrase=''):
        try:
            p12 = crypto.load_pkcs12(certificate.read(), passphrase)
            pub_cert = p12.get_certificate().to_cryptography()
            crt_bin = pub_cert.public_bytes(serialization.Encoding.DER).hex()
            address = CertificateClient().make_address_from_data(crt_bin)
        except ValueError:
            return {'error': 'Unable to load certificate entity'}, 422
        except crypto.Error:
            return {'error': 'Incorrect passphrase'}, 403

        return func(address)

    return validation_logic


def certificate_sign_request(func):
    def validation_logic(payload):
        try:
            certificate = x509.load_pem_x509_csr(payload['certificate'].encode('utf-8'),
                                                 default_backend())
            if not is_valid_token_balance():
                return {'error': 'You have no tokens to issue certificate'}, 402

            not_valid_before = payload.get('not_valid_before', None)
            not_valid_after = payload.get('not_valid_after', None)

            not_valid_before = datetime.datetime.fromtimestamp(not_valid_before) if not_valid_before else datetime.datetime.utcnow()
            not_valid_after = datetime.datetime.fromtimestamp(not_valid_after) if not_valid_after else not_valid_before + CERT_MAX_VALIDITY

            if not_valid_after:
                if not_valid_before >= not_valid_after:
                    return {'error': 'not_valid_before certificate property has to occur before the not_valid_after'}, 400
                if not_valid_after - not_valid_before > CERT_MAX_VALIDITY:
                    return {'error': 'The certificate validity exceeds the maximum value.'}, 400

        except ValueError:
            return {'error': 'Unable to load certificate request entity'}, 422

        return func(certificate, not_valid_before, not_valid_after)

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


def create_certificate(payload):
    parameters = get_params()
    encryption_algorithm = get_encryption_algorithm(payload)

    key = generate_key()
    key_export = generate_key_export(key, encryption_algorithm)
    cert = build_certificate(parameters, payload, key)

    return cert, key, key_export


def build_certificate(parameters, payload, key):
    name_oid = [x509.NameAttribute(NameOID.ORGANIZATION_NAME, CERT_ORGANIZATION),
                x509.NameAttribute(NameOID.USER_ID, CertificateClient().get_signer_pubkey())]

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
        not_valid_after = not_valid_before + CERT_MAX_VALIDITY

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
    return signer_balance >= CERT_STORE_PRICE


def certificate_already_exist(cert):
    account_client = AccountClient()
    address = account_client.make_address_from_data(cert.public_bytes(serialization.Encoding.DER).hex())
    try:
        value = account_client.get_value(address)
    except KeyNotFound:
        return False
    return True