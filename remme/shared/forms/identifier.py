from marshmallow import fields, validate

from .base import ProtoForm
from ._fields import IDField


class IdentifierForm(ProtoForm):
    id = IDField()


class IdentifiersForm(ProtoForm):
    ids = fields.List(IDField(error_messages={'required': 'Missed ids'}), required=True)
