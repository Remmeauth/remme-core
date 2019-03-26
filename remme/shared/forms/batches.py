from wtforms import fields, validators
from ._validators import StringTypeRequired
from .base import ProtoForm
from ._fields import IDField


class ListBatchesForm(ProtoForm):
    ids = fields.FieldList(IDField(validators=[
        validators.DataRequired(message='Missed ids'),
        StringTypeRequired(message='Incorrect identifier.'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]), min_entries=1)
    start = IDField()

    limit = fields.IntegerField(validators=[validators.DataRequired(message='Invalid limit field.'),
                                            validators.NumberRange(min=1, message='Invalid limit field.')],
                                )
    head = IDField()

    reverse = fields.BooleanField(validators=[
        validators.DataRequired(message='Invalid reverse field.'),
    ])
