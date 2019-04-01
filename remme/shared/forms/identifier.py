from wtforms import (
    fields,
    validators,
)
from remme.shared.forms.base import ProtoForm
from remme.shared.forms._fields import (
    BlockIDField,
    BatchIDField,
    TransactionIDField,
)


class BlockIdentifierForm(ProtoForm):
    id = BlockIDField()


class BatchIdentifierForm(ProtoForm):
    id = BatchIDField()


class TransactionIdentifierForm(ProtoForm):
    id = TransactionIDField()


class IdentifiersForm(ProtoForm):
    ids = fields.FieldList(BatchIDField(validators=[
        validators.DataRequired(message='Missed ids'),
        validators.Regexp('[0-9a-f]{128}',
                          message='Incorrect identifier.')
    ]), min_entries=1)
