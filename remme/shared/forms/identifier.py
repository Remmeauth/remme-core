from wtforms import fields, validators
from remme.shared.forms._fields import get_identifier_field

from .base import ProtoForm
from ._fields import IDField


class IdentifierForm(ProtoForm):
    id = IDField()


class BlockIdentifierForm(ProtoForm):
    id = get_identifier_field(message='Given block id is not a valid.')


class IdentifiersForm(ProtoForm):
    ids = fields.FieldList(IDField(validators=[
        validators.DataRequired(message='Missed ids'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]), min_entries=1)
