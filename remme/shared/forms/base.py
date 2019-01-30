import logging
from collections.abc import Mapping

from wtforms import Form

from werkzeug.datastructures import MultiDict
from remme.shared.utils import message_to_dict


logger = logging.getLogger(__name__)


class ProtoForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', data=None,
                 meta=None, **kwargs):
        self._wrong_fields = set()
        ignore_fields = kwargs.pop('ignore_fields', None)
        if ignore_fields is None:
            ignore_fields = []
        self._ignore_fields = ignore_fields

        if not isinstance(data, Mapping):
            data = None
        super().__init__(formdata, obj, prefix, data, meta, **kwargs)

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

    @property
    def wrong_fields(self):
        return self._wrong_fields.difference(self._ignore_fields)

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        super().process(formdata, obj, data, **kwargs)
        self._wrong_fields = set(kwargs.keys()).difference(self._fields.keys())

    def validate(self):
        if self.wrong_fields:
            self.errors['error'] = [f"Wrong params keys: {list(self.wrong_fields)}"]
            return False
        return super().validate()
