from marshmallow import (
    fields,
    validate,
    validates_schema,
    ValidationError,
)

from remme.protos.pub_key_pb2 import NewPubKeyPayload

from .base import ProtoForm
from ._validate import Choice
from ._fields import AddressField, RequiredString


class RSAConfigurationForm(ProtoForm):
    key = RequiredString()
    padding = fields.Field(
        required=True, validate=Choice(NewPubKeyPayload.RSAConfiguration.Padding.items()))


class ECDSAConfigurationForm(ProtoForm):
    key = RequiredString()
    ec = fields.Field(
        required=True, validate=Choice(NewPubKeyPayload.ECDSAConfiguration.EC.items()))


class Ed25519ConfigurationForm(ProtoForm):
    key = RequiredString()


class NewPublicKeyPayloadForm(ProtoForm):
    hashing_algorithm = fields.Field(
        required=True, validate=Choice(NewPubKeyPayload.HashingAlgorithm.items()))

    entity_hash = RequiredString()
    entity_hash_signature = RequiredString()

    valid_from = fields.Integer(required=True)
    valid_to = fields.Integer(required=True)

    rsa = fields.Nested(RSAConfigurationForm)
    ecdsa = fields.Nested(ECDSAConfigurationForm)
    ed25519 = fields.Nested(Ed25519ConfigurationForm)

    @validates_schema
    def validate_configuration(self, data):
        if all((cfg not in data for cfg in ['rsa', 'ecdsa', 'ed25519'])):
            raise ValidationError(
                'At least one of RSAConfiguration, ECDSAConfiguration or '
                'Ed25519Configuration must be set', ['configuration']
            )


class NewPubKeyStoreAndPayPayloadForm(ProtoForm):

    pub_key_payload = fields.Nested(NewPublicKeyPayloadForm, required=True)
    owner_public_key = fields.String(
        required=True, allow_none=False,
        validate=validate.Length(min=1, error='Missing data for required field.')
    )
    signature_by_owner = fields.String(
        required=True, allow_none=False,
        validate=validate.Length(min=1, error='Missing data for required field.')
    )


class RevokePubKeyPayloadForm(ProtoForm):
    address = AddressField()
