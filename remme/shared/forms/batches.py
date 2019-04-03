from wtforms import fields, validators
from ._validators import (
    StringTypeRequired,
    IntegerTypeRequired,
    BooleanTypeRequired,
    NotRequired,
)
from .base import ProtoForm


class ListBatchesForm(ProtoForm):

    def __init__(self, formdata=None, obj=None, prefix='', data=None,
                 meta=None, **kwargs):
        self._wrong_fields = set()
        ignore_fields = kwargs.pop('ignore_fields', None)
        if ignore_fields is None:
            ignore_fields = []
        self._ignore_fields = ignore_fields

        ids = kwargs.get('ids', None)

        if ids is None:
            pass
        elif type(ids) != list:
            raise validators.StopValidation('Invalid id.')
        elif len(ids) == 0:
            raise validators.StopValidation('Missed ids.')

        super().__init__(formdata, obj, prefix, data, meta, **kwargs)

    ids = fields.FieldList(
        fields.StringField(validators=[
            NotRequired(),
            StringTypeRequired(message='Invalid id.'),
            validators.Regexp('[0-9a-f]{128}', message='Invalid id.'),
        ]), min_entries=0)

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
