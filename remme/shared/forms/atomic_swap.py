from marshmallow import fields, validate

from .base import ProtoForm
from ._fields import AddressField, SwapIDField, RequiredString


class AtomicSwapInitPayloadForm(ProtoForm):
    receiver_address = AddressField()
    sender_address_non_local = RequiredString()
    amount = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1, error='Missing data for required field.'),
        error_messages={'required': 'Missing data for required field.'})
    swap_id = SwapIDField()
    secret_lock_by_solicitor = fields.String()
    email_address_encrypted_by_initiator = fields.String()
    created_at = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1, error='Missing data for required field.'),
        error_messages={'required': 'Missing data for required field.'})


class AtomicSwapApprovePayloadForm(ProtoForm):
    swap_id = SwapIDField()


class AtomicSwapExpirePayloadForm(ProtoForm):
    swap_id = SwapIDField()


class AtomicSwapSetSecretLockPayloadForm(ProtoForm):
    swap_id = SwapIDField()
    secret_lock = RequiredString()


class AtomicSwapClosePayloadForm(ProtoForm):
    swap_id = SwapIDField()
    secret_key = RequiredString()


class AtomicSwapForm(ProtoForm):
    swap_id = SwapIDField()
