from wtforms import fields, validators

from remme.protos.account_pb2 import TransferPayload
from remme.shared.forms.base import ProtoForm
from remme.shared.forms._fields import AddressField


class BlockInfoForm(ProtoForm):

    start = fields.IntegerField(default=0)
    limit = fields.IntegerField(default=0)
