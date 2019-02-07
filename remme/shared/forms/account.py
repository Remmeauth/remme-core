from marshmallow import fields, validate

from .base import ProtoForm
from ._fields import AddressField


class TransferPayloadForm(ProtoForm):
    address_to = AddressField(error_messages={'required': 'Missed address'})
    value = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1, error='Could not transfer with zero amount.'),
        error_messages={'required': 'Could not transfer with zero amount.'})


class GenesisPayloadForm(ProtoForm):
    total_supply = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1, error='Could not transfer with zero amount.'),
        error_messages={'required': 'Could not transfer with zero amount.'})


def get_address_form(name):
    """Dynamicly set address field to generated form class
    """
    return type('AddressForm', (ProtoForm,), {
        name: AddressField()
    })
