
from wtforms import fields, validators
from wtforms import Form

from remme.shared.forms._fields import AddressField
from werkzeug.datastructures import MultiDict


class GenericExcessParametersForm(Form):

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        self.formdata = formdata
        super().process(formdata, obj, data, **kwargs)

    def validate(self):
        is_valid = super().validate()

        for form_parameter_name in self.formdata.keys():
            if form_parameter_name not in self:

                if is_valid:
                    is_valid = False

                msg = [f'Excess request parameter.']
                self.errors[form_parameter_name] = msg

        return is_valid


class SendTokensForm(GenericExcessParametersForm):
    public_key_address = AddressField()


def test_excess_form_parameter():
    request_params = {
        'public_key_address': '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30',
        'some_excess_parameter': 10,
    }

    form = SendTokensForm(MultiDict(request_params))

    assert not form.validate()
    assert form.errors == {
        'some_excess_parameter': ['Excess request parameter.'],
    }


def test_ok_form_parameter():
    request_params = {
        'public_key_address': '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30',
    }

    form = SendTokensForm(MultiDict(request_params))

    assert form.validate()
    assert form.errors == {}
