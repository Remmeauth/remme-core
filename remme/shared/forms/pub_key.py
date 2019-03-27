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

    rsa = fields.FormField(RSAConfigurationForm)
    ecdsa = fields.FormField(ECDSAConfigurationForm)
    ed25519 = fields.FormField(Ed25519ConfigurationForm)

    def validate(self):
        is_valid = super().validate()
        pt_error_keys = ['rsa', 'ecdsa', 'ed25519']
        if all((ek in self.errors for ek in pt_error_keys)):
            msg = ['At least one of RSAConfiguration, ECDSAConfiguration or '
                   'Ed25519Configuration must be set']
            self._errors['configuration'] = msg
            for cfg in pt_error_keys:
                del self._errors[cfg]
            is_valid = False
        else:
            for ek in pt_error_keys:
                if ek not in self.errors:
                    cp_errs = pt_error_keys[:]
                    cp_errs.remove(ek)
                    for cfg in cp_errs:
                        del self._errors[cfg]
                    if not self._errors:
                        is_valid = True
                    break

        return is_valid


class NewPubKeyStoreAndPayPayloadForm(ProtoForm):

    pub_key_payload = fields.FormField(NewPublicKeyPayloadForm)
    owner_public_key = fields.StringField(validators=[validators.DataRequired()])
    signature_by_owner = fields.StringField(validators=[validators.DataRequired()])


class RevokePubKeyPayloadForm(ProtoForm):
    address = AddressField()
