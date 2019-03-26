# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
import logging

from remme.clients.account import AccountClient
from remme.rpc_api.utils import validate_params
from remme.shared.forms import get_address_form

__all__ = (
    'get_balance',
    'get_public_keys_list',
)

logger = logging.getLogger(__name__)

client = AccountClient()

from aiohttp_json_rpc import RpcInvalidParamsError
from remme.shared.forms._fields import AddressField
from werkzeug.datastructures import MultiDict
from wtforms import Form


class ValidateExcessIncomingParameters(Form):

    def __init__(self, formdata=None, obj=None, prefix='', data=None, meta=None, **kwargs):
        self.excess_incoming_parameters = []
        super().__init__(formdata, obj, prefix, data, meta, **kwargs)

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        """
        Process the form data.

        The one of the goals of the form is to detect excess incoming parameters.
        If these parameters are presented, return according error message.
        """
        super().process(formdata, obj, data, **kwargs)

        passed_to_form_parameters_keys = formdata.to_dict().keys()
        existing_form_fields_keys = dict(self._fields).keys()

        for passed_key in passed_to_form_parameters_keys:
            if passed_key not in existing_form_fields_keys:
                self.excess_incoming_parameters.append(passed_key)

    def validate(self):
        """
        Validate the form data.

        If excess incoming parameters are presented, add excess incoming parameters error message with
        the list of these parameters.
        """
        if self.excess_incoming_parameters:
            self.errors['error'] = [
                f'Wrong params keys: {self.excess_incoming_parameters}',
            ]
            return False

        return super().validate()


class GetAccountBalanceForm(ValidateExcessIncomingParameters):

    public_key_address = AddressField()


async def get_balance(request):
    """
    Get account balance by account address from public key.
    """
    form = GetAccountBalanceForm(MultiDict(request.params))

    if not form.validate():
        raise RpcInvalidParamsError(message=form.errors)

    return await client.get_balance(address=form.public_key_address.data)


@validate_params(get_address_form('public_key_address'))
async def get_public_keys_list(request):
    address = request.params['public_key_address']
    return await client.get_pub_keys(address)
