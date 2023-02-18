import aiohttp
from lxml.etree import HTML, ElementBase
from yarl import URL

from .common import first
from .log import LOGGER


class _Submit:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        html: ElementBase | str,
        encoding: str = "utf-8",
    ):
        self.html = html
        self.encoding = encoding
        self.session = session

    def __await__(self) -> aiohttp.ClientResponse:
        return self._submit().__await__()

    async def __aenter__(self):
        self._response = await self._submit()
        return self._response

    async def __aexit__(self, *args):
        await self._response.release()

    async def _submit(self):
        html = self.html
        encoding = self.encoding
        if isinstance(html, str):
            html = HTML(html.encode(encoding))

        url = URL(first(html.xpath("//form/@action")))
        method = first(html.xpath("//form/@method"), "get").lower()
        data = {
            first(input.xpath("@name")): first(input.xpath("@value"))
            for input in html.xpath("//input")
        }
        LOGGER.debug(f"Submitting {method.upper()} {url}")
        return await getattr(self.session, method)(url, data=data)


def submit(session: aiohttp.ClientSession, html: ElementBase | str, encoding="utf-8"):
    return _Submit(session, html, encoding)
