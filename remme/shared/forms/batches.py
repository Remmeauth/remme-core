from wtforms import fields, validators
from ._validators import (
    StringTypeRequired,
    IntegerTypeRequired,
    BooleanTypeRequired,
)
from .base import ProtoForm
from ._fields import IDField


class ListBatchesForm(ProtoForm):
    ids = fields.FieldList(
        IDField(validators=[
        StringTypeRequired(message='Invalid id.'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Invalid id.'),
    ]), min_entries=1)
    start = IDField()

    limit = fields.IntegerField(validators=[validators.DataRequired(message='Invalid limit count.'),
                                            IntegerTypeRequired(message='Invalid limit count.'),
                                            validators.NumberRange(min=1, message='Invalid limit count.')],
                                )
    head = IDField()

    reverse = fields.BooleanField(validators=[
        validators.DataRequired(message='Incorrect identifier.'),
        BooleanTypeRequired(message='Incorrect identifier.')
    ])

    def __init__(self, formdata=None, obj=None, prefix='', data=None,
                 meta=None, **kwargs):
        self._wrong_fields = set()
        ignore_fields = kwargs.pop('ignore_fields', None)
        if ignore_fields is None:
            ignore_fields = []
        self._ignore_fields = ignore_fields

        ids = kwargs.get('ids', None)

        if ids is None:
            raise validators.StopValidation('Missed ids.')
        if type(ids) != list:
            raise validators.StopValidation('Invalid id.')

        super().__init__(formdata, obj, prefix, data, meta, **kwargs)



