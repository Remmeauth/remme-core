from wtforms import fields, validators

from .base import ProtoForm


class NodePKForm(ProtoForm):
    private_key = fields.StringField(validators=[
        validators.DataRequired(message='Missed private_key'),
        validators.Regexp('[0-9a-f]{64}',
                          message='Incorrect private key.')
    ])
