from wtforms import fields, validators

from .base import ProtoForm
from ._fields import AddressField

from remme.protos.account_pb2 import TransferPayload


class TransferPayloadForm(ProtoForm):

    sender_account_type = fields.SelectField(choices=TransferPayload.SenderAccountType.items())

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

    setattr(AddressForm, name, AddressField())
    return AddressForm
