from wtforms import fields, validators

from .base import ProtoForm

from remme.shared.forms._fields import (
    AddressField,
    PublicKeyAddressField,
)


class TransferPayloadForm(ProtoForm):
    address_to = AddressField()
    value = fields.IntegerField(validators=[
        validators.DataRequired(message='Could not transfer with zero amount.')
    ])


class GenesisPayloadForm(ProtoForm):
    total_supply = fields.IntegerField(validators=[validators.DataRequired()])


def get_address_form(name):
    """Dynamicly set address field to generated form class
    """
    class AddressForm(ProtoForm):
        pass

    setattr(AddressForm, name, PublicKeyAddressField())
    return AddressForm
