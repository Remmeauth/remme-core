from wtforms import (
    fields,
    validators,
)
from remme.shared.forms.base import ProtoForm
from remme.shared.forms._fields import (
    BlockIDField,
    IDField,
)


class BlockIdentifierForm(ProtoForm):
    id = BlockIDField()


class IdentifierForm(ProtoForm):
    id = IDField()


class IdentifiersForm(ProtoForm):
    ids = fields.FieldList(IDField(validators=[
        validators.DataRequired(message='Missed ids'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]), min_entries=1)
