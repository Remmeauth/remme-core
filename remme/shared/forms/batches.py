from wtforms import fields, validators

from .base import ProtoForm
from ._fields import IDField


class ListBatchesForm(ProtoForm):
    ids = fields.FieldList(IDField(validators=[
        validators.DataRequired(message='Missed ids'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]), min_entries=1)
    start = IDField()
    limit = fields.IntegerField(validators=[validators.DataRequired()], min=1)
    head = IDField()
    reverse = fields.BooleanField()
