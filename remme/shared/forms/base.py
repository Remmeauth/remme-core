import logging
from collections.abc import Mapping

from marshmallow import Schema

from remme.shared.utils import message_to_dict


logger = logging.getLogger(__name__)


class ProtoForm(Schema):

    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=strict, **kwargs)

    # def __init__(self, **kwargs):
    #     self._wrong_fields = set()
    #     ignore_fields = kwargs.pop('ignore_fields', None)
    #     if ignore_fields is None:
    #         ignore_fields = []
    #     self._ignore_fields = ignore_fields

    #     if not isinstance(data, Mapping):
    #         data = None
    #     super().__init__(formdata, obj, prefix, data, meta, **kwargs)

    def load_proto(self, pb):
        data = message_to_dict(pb)
        return self.load(data)

    # def get_pb_class(self):
    #     return getattr(self, '_pb_class', None)

    # @property
    # def wrong_fields(self):
    #     return self._wrong_fields.difference(self._ignore_fields)

    # def process(self, formdata=None, obj=None, data=None, **kwargs):
    #     super().process(formdata, obj, data, **kwargs)
    #     self._wrong_fields = set(kwargs.keys()).difference(self._fields.keys())

    # def validate(self):
    #     if self.wrong_fields:
    #         self.errors['error'] = [f"Wrong params keys: {list(self.wrong_fields)}"]
    #         return False
    #     return super().validate()
