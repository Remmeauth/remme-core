from wtforms import fields, validators

from remme.protos.pub_key_pb2 import NewPubKeyPayload
from .base import ProtoForm
from ._fields import AddressField


class RSAConfigurationForm(ProtoForm):
    key = fields.StringField(validators=[validators.DataRequired()])
    padding = fields.SelectField(choices=NewPubKeyPayload.RSAConfiguration.Padding.items())


class ECDSAConfigurationForm(ProtoForm):
    key = fields.StringField(validators=[validators.DataRequired()])
    ec = fields.SelectField(choices=NewPubKeyPayload.ECDSAConfiguration.EC.items())


class Ed25519ConfigurationForm(ProtoForm):
    key = fields.StringField(validators=[validators.DataRequired()])


class NewPublicKeyPayloadForm(ProtoForm):
    hashing_algorithm = fields.SelectField(choices=NewPubKeyPayload.HashingAlgorithm.items())

    entity_hash = fields.StringField(validators=[validators.DataRequired()])
    entity_hash_signature = fields.StringField(validators=[validators.DataRequired()])

    valid_from = fields.IntegerField(validators=[validators.DataRequired()])
    valid_to = fields.IntegerField(validators=[validators.DataRequired()])

    rsa = fields.FieldList(fields.FormField(RSAConfigurationForm), max_entries=1)
    ecdsa = fields.FieldList(fields.FormField(ECDSAConfigurationForm), max_entries=1)
    ed25519 = fields.FieldList(fields.FormField(Ed25519ConfigurationForm), max_entries=1)

    def validate(self):
        is_valid = super().validate()
        if not self.rsa.data and not self.ecdsa.data and not self.ed25519.data:
            msg = ['At least one of RSAConfiguration, ECDSAConfiguration or '
                   'Ed25519Configuration must be set']
            self.errors['configuration'] = msg
            is_valid = False
        return is_valid


class RevokePubKeyPayloadForm(ProtoForm):
    address = AddressField()
