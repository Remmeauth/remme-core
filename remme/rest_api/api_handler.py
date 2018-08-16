import asyncio
import logging

from aiohttp import web
from connexion.apis.aiohttp_api import AioHttpApi
from connexion.lifecycle import ConnexionResponse


logger = logging.getLogger('connexion.apis.aiohttp_api')


class AioHttpApi(AioHttpApi):

    @classmethod
    @asyncio.coroutine
    def get_response(cls, response, mimetype=None, request=None):
        """Get response.
        This method is used in the lifecycle decorators
        :rtype: aiohttp.web.Response
        """
        while asyncio.iscoroutine(response):
            response = yield from response

        if isinstance(response, tuple) and isinstance(response[0], dict):
            response = web.json_response(response[0], status=response[1])
        elif isinstance(response, dict):
            response = web.json_response(response)

        url = str(request.url) if request else ''

        logger.debug('Getting data and status code',
                     extra={
                         'data': response,
                         'url': url
                     })

        if isinstance(response, ConnexionResponse):
            response = cls._get_aiohttp_response_from_connexion(response, mimetype)

        logger.debug('Got data and status code (%d)',
                     response.status, extra={'data': response.body, 'url': url})

        return response
