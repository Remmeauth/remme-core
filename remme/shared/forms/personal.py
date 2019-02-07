from marshmallow import fields, validate

from .base import ProtoForm


class NodePKForm(ProtoForm):
    private_key = fields.String(
        required=True, error_messages={'required': 'Missed private_key'},
        validate=validate.Regexp(r'[0-9a-f]{64}', error='Incorrect atomic swap identifier.')
    )
