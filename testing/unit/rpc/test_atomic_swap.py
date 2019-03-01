
import pytest


from remme.rpc_api.atomic_swap import get_atomic_swap_info

@pytest.mark.asyncio
async def test_():

    class Request:

        @property
        def params(self):
            return {
                'swap_id': 0,
            }

    request = Request()

    result = get_atomic_swap_info(request)

    print(result)

    assert 1 == 2
