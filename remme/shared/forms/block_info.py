from wtforms import fields

from remme.shared.forms.base import ProtoForm
from remme.shared.forms._validators import Optional


class IntegersForm(ProtoForm):

    start = fields.IntegerField(validators=[Optional(message='Incorrect parameter identifier.')])
    limit = fields.IntegerField(validators=[Optional(message='Incorrect parameter identifier.')])
