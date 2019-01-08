from wtforms import fields, validators

from .base import ProtoForm
from ._fields import AddressField


class TransferPayloadForm(ProtoForm):
    address_to = AddressField()
    value = fields.IntegerField(validators=[validators.DataRequired()])


class GenesisPayloadForm(ProtoForm):
    total_supply = fields.IntegerField(validators=[validators.DataRequired()])
