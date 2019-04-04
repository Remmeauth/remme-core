import re

from wtforms import (
    fields,
    validators,
)

from remme.shared.forms.base import ProtoForm


class ListStateForm(ProtoForm):

    address = fields.StringField()
    start = fields.StringField()
    limit = fields.IntegerField()
    head = fields.StringField()
    reverse = fields.StringField()

    def validate_address(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, str):
            raise validators.StopValidation('Address is not of a blockchain token type.')

        if re.match(r'^[0-9a-f]{70}$', field.data) is None:
            raise validators.StopValidation('Address is not of a blockchain token type.')

    def validate_start(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, str):
            raise validators.StopValidation('Address is not of a blockchain token type.')

        if re.match(r'^[0-9a-f]{70}$', field.data) is None:
            raise validators.StopValidation('Address is not of a blockchain token type.')

    def validate_limit(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, int) or isinstance(field.data, bool):
            raise validators.StopValidation('Invalid limit count.')

    def validate_head(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, str):
            raise validators.StopValidation('Given block id is not a valid.')

        if re.match(r'^[0-9a-f]{128}$', field.data) is None:
            raise validators.StopValidation('Given block id is not a valid.')

    def validate_reverse(form, field):
        if not field.data and not isinstance(field.data, int):
            return

        if field.data != 'false':
            raise validators.StopValidation('Incorrect reverse identifier.')
