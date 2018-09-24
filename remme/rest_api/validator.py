import logging
from urllib.parse import urljoin

import aiohttp
from aiohttp import web

from remme.clients.basic import BasicClient


logger = logging.getLogger(__name__)


PROXY_TIMEOUT = 5


async def proxy(request):
    client = BasicClient(None)
    target_url = urljoin(client.url, request.match_info['path'])

    data = await request.read()
    get_data = request.rel_url.query

    logger.debug("-----------------------------------------------------------")
    logger.debug("REQUEST C2P")
    logger.debug("-----------------------------------------------------------")
    logger.debug("URL | HEADER | METHOD | DATA | GET DATA")
    logger.debug("-----------------------------------------------------------")
    logger.debug(f"{target_url} | {request.headers} | {request.method} | "
                 f"{data} | {get_data}")

    async with aiohttp.ClientSession() as session:
        async with session.request(request.method, target_url,
                                   headers=request.headers, params=get_data,
                                   data=data, timeout=PROXY_TIMEOUT) as res:
            raw = await res.read()

    logger.debug("-----------------------------------------------------------")
    logger.debug("RESPONSE P2C")
    logger.debug("-----------------------------------------------------------")
    logger.debug(f"Header {res.headers} | Status {res.status}")
    logger.debug("-----------------------------------------------------------")

    return web.Response(body=raw, status=res.status, headers=res.headers)
