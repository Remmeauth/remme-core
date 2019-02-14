from wtforms import fields, validators

from .base import ProtoForm
from ._fields import AddressField, SwapIDField


class AtomicSwapInitPayloadForm(ProtoForm):
    receiver_address = AddressField()
    sender_address_non_local = fields.StringField(validators=[validators.DataRequired()])
    amount = fields.IntegerField(validators=[validators.DataRequired()])
    swap_id = SwapIDField()
    secret_lock_by_solicitor = fields.StringField(validators=[validators.Optional()])
    email_address_encrypted_by_initiator = fields.StringField(validators=[validators.Optional()])
    created_at = fields.IntegerField(validators=[validators.DataRequired()])


class AtomicSwapApprovePayloadForm(ProtoForm):
    swap_id = SwapIDField()


class AtomicSwapExpirePayloadForm(ProtoForm):
    swap_id = SwapIDField()


class AtomicSwapSetSecretLockPayloadForm(ProtoForm):
    swap_id = SwapIDField()
    secret_lock = fields.StringField(validators=[validators.DataRequired()])


class AtomicSwapClosePayloadForm(ProtoForm):
    swap_id = SwapIDField()
    secret_key = fields.StringField(validators=[validators.DataRequired()])


class AtomicSwapForm(ProtoForm):
    swap_id = SwapIDField()
