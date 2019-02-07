
import pytest

from remme.rpc_api.pkc import get_node_config


class ExcessParametersRequest:

    @property
    def params(self):
        return {
            'some_excess_parameter': 10,
        }


@pytest.mark.asyncio
async def test_excess_form_parameter():

    result = await get_node_config(request=ExcessParametersRequest())

    # form = SendTokensForm(MultiDict(request_params))

    # assert not form.validate()
    assert result == {
        'some_excess_parameter': ['Excess request parameter.'],
    }


# def test_ok_form_parameter():
#     request_params = {
#         'public_key_address': '112007b9433e1da5c624ff926477141abedfd57585a36590b0a8edc4104ef28093ee30',
#     }
#
#     form = SendTokensForm(MultiDict(request_params))
#
#     assert form.validate()
#     assert form.errors == {}
#
#
#