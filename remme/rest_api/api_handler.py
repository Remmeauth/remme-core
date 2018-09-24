import asyncio
import logging
from urllib.parse import parse_qs

from aiohttp import web
from connexion.handlers import AuthErrorHandler

from connexion import NoContent
from connexion.apis.aiohttp_api import AioHttpApi, _HttpNotFoundError
from connexion.lifecycle import ConnexionRequest, ConnexionResponse


logger = logging.getLogger('connexion.apis.aiohttp_api')


class AioHttpApi(AioHttpApi):

    def add_auth_on_not_found(self, security, security_definitions):
        """
        Adds a 404 error handler to authenticate and only expose the 404 status if the security validation pass.
        """
        logger.debug('Adding path not found authentication')
        not_found_error = AuthErrorHandler(
            self, _HttpNotFoundError(),
            security=security,
            security_definitions=security_definitions
        )
        endpoint_name = "{}_not_found".format(self._api_name)
        self.cors.add(self.subapp.router.add_route(
            '*',
            '/{not_found_path}',
            not_found_error.function,
            name=endpoint_name
        ))

    def _add_operation_internal(self, method, path, operation):
        method = method.upper()
        operation_id = operation.operation_id or path

        logger.debug('... Adding %s -> %s', method, operation_id,
                     extra=vars(operation))

        handler = operation.function
        endpoint_name = '{}_{}_{}'.format(
            self._api_name,
            AioHttpApi.normalize_string(path),
            method.lower()
        )
        self.cors.add(self.subapp.router.add_route(
            method, path, handler, name=endpoint_name
        ))

        if not path.endswith('/'):
            self.cors.add(self.subapp.router.add_route(
                method, path + '/', handler, name=endpoint_name + '_'
            ))

    @classmethod
    async def get_request(cls, req):
        """Convert aiohttp request to connexion

        :param req: instance of aiohttp.web.Request
        :return: connexion request instance
        :rtype: ConnexionRequest
        """
        url = str(req.url)
        logger.debug('Getting data and status code',
                     extra={'has_body': req.has_body, 'url': url})
        query = parse_qs(req.rel_url.query_string)
        headers = {k.decode(): v.decode() for k, v in req.raw_headers}
        body = None
        if req.can_read_body:
            body = await req.read()

        return ConnexionRequest(url=url,
                                method=req.method.lower(),
                                path_params=dict(req.match_info),
                                query=query,
                                headers=headers,
                                body=body,
                                json_getter=lambda: cls.jsonifier.loads(body),
                                files={},
                                context=req)

    @staticmethod
    def _json_response(response, status=200):
        if isinstance(response, web.Response):
            return response

        if response is NoContent:
            return web.Response(status=status)
        return web.json_response(response, status=status)

    @classmethod
    async def get_response(cls, response, mimetype=None, request=None):
        """Get response.
        This method is used in the lifecycle decorators
        :rtype: aiohttp.web.Response
        """
        while asyncio.iscoroutine(response):
            response = await response

        logger.debug('Getting data', extra={'data': response})

        if isinstance(response, ConnexionResponse):
            response = cls._get_aiohttp_response_from_connexion(response,
                                                                mimetype)
        elif isinstance(response, tuple):
            response = cls._json_response(response[0], response[1])
        else:
            response = cls._json_response(response)

        url = str(request.url) if request else ''
        logger.debug('Got data and status code (%d)', response.status,
                     extra={'data': response.body, 'url': url})

        return response
