from wtforms import fields, validators


class AddressField(fields.StringField):

    validators = [
        validators.DataRequired(),
        validators.Regexp('[0-9a-f]{70}',
                          message='Address is not of a blockchain token type.')
    ]
