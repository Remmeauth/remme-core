from wtforms import fields, validators
from ._validators import (
    StringTypeRequired,
    IntegerTypeRequired,
    BooleanTypeRequired,
    NotRequired,
)
from .base import ProtoForm
import re

class ListBatchesForm(ProtoForm):

    ids = fields.StringField()

    if isinstance(ids, list):
        ids = fields.FieldList(fields.StringField(), min_entries=0)

    @staticmethod
    def validate_ids(form, field):
        if field.data is None:
            return

        if not isinstance(field.data, list):
            raise validators.StopValidation('Invalid id.')

        for data in field.data:

            if not isinstance(data, str):
                raise validators.StopValidation('Invalid id.')

            if re.match(r'^[0-9a-f]{128}$', data) is None:
                raise validators.StopValidation('Invalid id.')

    start = fields.StringField(validators=[
        NotRequired(),
        StringTypeRequired(message='Invalid id.'),
        validators.Regexp(regex='[0-9a-f]{128}',  message='Invalid id.')
    ])

    limit = fields.IntegerField(validators=[NotRequired(),
                                            IntegerTypeRequired(message='Invalid limit count.'),
                                            validators.NumberRange(min=1, message='Invalid limit count.')],
                                )

    head = fields.StringField(validators=[
        NotRequired(),
        StringTypeRequired(message='Invalid id.'),
        validators.Regexp(regex='[0-9a-f]{128}',  message='Invalid id.')
    ])

    reverse = fields.IntegerField(validators=[
        NotRequired(),
        BooleanTypeRequired(message='Incorrect identifier.')
    ])
