from wtforms import fields, validators

from remme.shared.forms._validators import AddressTypeRequired


class AddressField(fields.StringField):

    validators = [
        validators.DataRequired(message='Missed address.'),
        AddressTypeRequired(message='Address is not of a blockchain token type.'),
        validators.Regexp(
            regex='[0-9a-f]{70}',
            message='Address is not of a blockchain token type.',
        ),
    ]


class SwapIDField(fields.StringField):

    validators = [
        validators.DataRequired(message='Missed swap_id'),
        validators.Regexp('[0-9a-f]{64}',
                          message='Incorrect atomic swap identifier.')
    ]


class IDField(fields.StringField):

    validators = [
        validators.DataRequired(message='Missed id'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]
