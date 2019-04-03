from wtforms import fields, validators

from .base import ProtoForm


class NodeAccountInternalTransferPayloadForm(ProtoForm):
    value = fields.IntegerField(validators=[
        validators.DataRequired(message='Could not transfer with zero amount.')
    ])


class NodeAccountGenesisForm(ProtoForm):
    value = fields.IntegerField()


class SetBetPayloadForm(ProtoForm):
    fixed_amount = fields.FloatField(validators=[
        validators.DataRequired()
    ])
    min = fields.BooleanField(validators=[
        validators.DataRequired()
    ])
    max = fields.BooleanField(validators=[
        validators.DataRequired()
    ])

    def validate(self):
        is_valid = super().validate()
        pt_error_keys = ['fixed_amount', 'min', 'max']
        if all((ek in self.errors for ek in pt_error_keys)):
            msg = ['At least one of fixed_amount, min or '
                   'max must be set']
            self._errors['bet'] = msg
            for cfg in pt_error_keys:
                del self._errors[cfg]
            is_valid = False
        else:
            for ek in pt_error_keys:
                if ek not in self.errors:
                    cp_errs = pt_error_keys[:]
                    cp_errs.remove(ek)
                    for cfg in cp_errs:
                        del self._errors[cfg]
                    if not self._errors:
                        is_valid = True
                    break

        return is_valid