from marshmallow import (
    fields, validate,
)


class RequiredString(fields.String):

    def __init__(
        self, required=True, allow_none=False,
        validate=validate.Length(min=1, error='Missing data for required field.'),
        **kwargs
    ):
        super().__init__(required=required, allow_none=allow_none, validate=validate, **kwargs)


class AddressField(fields.String):

    default_error_messages = {
        'required': 'Missed address',
    }

    def __init__(self, required=True, validate=[
        validate.Regexp(r'[0-9a-f]{70}', error='Address is not of a blockchain token type.')
    ], *args, **kwargs):
        super().__init__(required=required, validate=validate, *args, **kwargs)


class SwapIDField(fields.String):

    default_error_messages = {
        'required': 'Missed swap_id',
    }

    def __init__(self, required=True, validate=[
        validate.Regexp(r'[0-9a-f]{64}', error='Incorrect atomic swap identifier.')
    ], *args, **kwargs):
        super().__init__(required=required, validate=validate, *args, **kwargs)


class IDField(fields.String):

    default_error_messages = {
        'required': 'Missed id',
    }

    def __init__(self, required=True, validate=[
        validate.Regexp(r'[0-9a-f]{128}', error='Incorrect identifier.')
    ], *args, **kwargs):
        super().__init__(required=required, validate=validate, *args, **kwargs)
