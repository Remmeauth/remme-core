from wtforms import fields, validators

from .base import ProtoForm
from ._fields import AddressField


class TransferPayloadForm(ProtoForm):
    address_to = AddressField()
    value = fields.IntegerField(validators=[validators.DataRequired()])


class GenesisPayloadForm(ProtoForm):
    total_supply = fields.IntegerField(validators=[validators.DataRequired()])


def get_address_form(name):
    """Dynamicly set address field to generated form class
    """
    class AddressForm(ProtoForm):
        pass

    setattr(AddressForm, name, AddressField())
    return AddressForm
