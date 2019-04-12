import re

from wtforms import (
    fields,
    validators,
)

from remme.shared.forms.base import ProtoForm

FAMILY_NAMES = ['account', 'node_account', 'pub_key', 'AtomicSwap']


class ListTransactionsForm(ProtoForm):

    ids = fields.StringField()

    if isinstance(ids, list):
        ids = fields.FieldList(unbound_field=fields.StringField(), min_entries=1)

    start = fields.StringField()
    limit = fields.IntegerField()
    head = fields.StringField()
    reverse = fields.StringField()
    family_name = fields.StringField()

    def validate_ids(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, list):
            raise validators.StopValidation('Header signature is not of a blockchain token type.')

        for data in field.data:

            if not isinstance(data, str):
                raise validators.StopValidation('Header signature is not of a blockchain token type.')

            if re.match(r'^[0-9a-f]{128}$', data) is None:
                raise validators.StopValidation('Header signature is not of a blockchain token type.')

    def validate_start(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, str):
            raise validators.StopValidation('Header signature is not of a blockchain token type.')

        if re.match(r'^[0-9a-f]{128}$', field.data) is None:
            raise validators.StopValidation('Header signature is not of a blockchain token type.')

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

    def validate_family_name(form, field):
        if field.data is None:
            return

        if field.data not in FAMILY_NAMES:
            raise validators.StopValidation('Incorrect family name.')


class ListReceiptsForm(ProtoForm):

    ids = fields.StringField()

    if isinstance(ids, list):
        ids = fields.FieldList(fields.StringField(), min_entries=1)

    @staticmethod
    def validate_ids(form, field):
        if field.data == '' or field.data is None:
            raise validators.StopValidation('Missed list of identifiers.')

        if not isinstance(field.data, list):
            raise validators.StopValidation('Incorrect identifier.')

        for data in field.data:

            if not isinstance(data, str):
                raise validators.StopValidation('Incorrect identifier.')

            if re.match(r'^[0-9a-f]{128}$', data) is None:
                raise validators.StopValidation('Incorrect identifier.')
