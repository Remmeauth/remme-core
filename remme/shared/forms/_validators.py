from wtforms import validators


class StringTypeRequired(object):
    """
    Validates the value for the required type.

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
