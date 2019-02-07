from marshmallow import validate, ValidationError


class Choice(validate.OneOf):

    def __call__(self, value):
        choices = dict(self.choices)
        if value not in choices:
            raise ValidationError(self._format_error(value))

        return choices[value]
