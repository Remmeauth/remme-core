from wtforms import fields, validators


class AddressField(fields.StringField):

    validators = [
        validators.InputRequired(message='Missed address'),
        validators.Regexp('[0-9a-f]{70}',
                          message='Address is not of a blockchain token type.')
    ]


class SwapIDField(fields.StringField):

    validators = [
        validators.InputRequired(message='Missed swap_id'),
        validators.Regexp('[0-9a-f]{64}',
                          message='Incorrect atomic swap identifier.')
    ]


class IDField(fields.StringField):

    validators = [
        validators.InputRequired(message='Missed id'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]
