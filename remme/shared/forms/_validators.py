from wtforms import validators

import logging

logger = logging.getLogger(__name__)


class StringTypeRequired(object):
    """
    Validates the value for the required string type.

    Args:
        message (str): error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):

        if not isinstance(field.data, str):
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)


class IntegerTypeRequired(object):
    """
    Validates the value for the required integer type.

    Args:
        message (str): error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):

        if field.data is None:
            return

        if not isinstance(field.data, int) or isinstance(field.data, bool):

            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)


class DataRequired(object):
    """
    Checks the field's data is 'truthy' otherwise stops the validation chain.

    This validator checks that the ``data`` attribute on the field is a 'true'
    value (effectively, it does ``if field.data``.) Furthermore, if the data
    is a string type, a string containing only whitespace characters is
    considered false.

    If the data is zero, WTForms validators.DataRequired considers it like False
    and response is like argument is missed. We need not missed argument error message,
    but invalid data error message. So appeared the opportunity to write сustom
    validator to solve this case.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    Args:
        message (str): error message to raise in case of a validation error.
    """

    field_flags = ('required',)

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):

        if field.data == 0:
            return

        elif not field.data or isinstance(field.data, str) and not field.data.strip():
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)
