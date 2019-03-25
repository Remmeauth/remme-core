from wtforms import validators
from wtforms.fields import IntegerField

from remme.shared.forms.base import ProtoForm
from remme.shared.forms._validators import IntegerTypeRequired


class IntegerForm(ProtoForm):

    start = IntegerField('Start', validators=[
        IntegerTypeRequired(message='Incorrect parameter identifier.'), validators.optional(),
    ])
    limit = IntegerField('Limit', validators=[
        IntegerTypeRequired(message='Incorrect parameter identifier.'), validators.optional(),
    ])
