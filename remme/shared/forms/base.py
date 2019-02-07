from collections.abc import Mapping

from wtforms import Form

from werkzeug.datastructures import MultiDict
from remme.shared.utils import message_to_dict


class ProtoForm(Form):

    @classmethod
    def load_proto(cls, pb):
        data = message_to_dict(pb)
        form = cls.load_data(data)
        form._pb_class = pb.__class__
        return form

    @classmethod
    def load_data(cls, data):
        formdata = MultiDict(data)
        form = cls(formdata)
        for k, v in data.items():
            if not isinstance(v, Mapping):
                continue
            try:
                field = getattr(form, k)
            except AttributeError:
                continue
            field.append_entry(v)
        return form

    def get_pb_class(self):
        return getattr(self, '_pb_class', None)


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
