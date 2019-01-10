"""
Provide utils for async functions handling.
"""


async def return_async_value(value):
    """
    Asynchronous function return value impostor.

    Using for mock particular asynchronous function with specified return value.

    Example of usage in code:
        mock_get_directory_children_by_id = mock.patch(
            'bridge.database.services.directory.children.get.GetDirectoryChildren.by_id'
        )
        mock_get_directory_children_by_id.return_value = return_async_value({'id': 15})

    References:
        - https://github.com/pytest-dev/pytest-mock/issues/60
    """
    return value
