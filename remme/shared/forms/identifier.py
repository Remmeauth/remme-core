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
