from wtforms import (
    fields,
    validators,
)

from remme.shared.forms._validators import (
    DataRequired,
    StringTypeRequired,
)


class AddressField(fields.StringField):

    validators = [
        DataRequired(message='Missed address.'),
        StringTypeRequired(message='Address is not of a blockchain token type.'),
        validators.Regexp(regex='[0-9a-f]{70}', message='Address is not of a blockchain token type.'),
    ]


class SwapIDField(fields.StringField):

    validators = [
        DataRequired(message='Missed swap_id.'),
        StringTypeRequired(message='Given swap_id is not a valid.'),
        validators.Regexp(regex='[0-9a-f]{64}', message='Given swap_id is not a valid.')
    ]


class IDField(fields.StringField):

    validators = [
        DataRequired(message='Missed id.'),
        StringTypeRequired(message='Given batch id is not a valid.'),
        validators.Regexp(regex='[0-9a-f]{128}',  message='Given batch id is not a valid.')
    ]


class BlockIDField(fields.StringField):

    validators = [
        DataRequired(message='Missed id.'),
        StringTypeRequired(message='Given block id is not a valid.'),
        validators.Regexp(regex='[0-9a-f]{128}', message='Given block id is not a valid.')
    ]
