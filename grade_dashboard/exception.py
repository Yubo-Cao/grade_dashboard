import aiohttp


class SpiderIOException(Exception):
    def __init__(
        self,
        message: str,
        response: aiohttp.ClientResponse,
        text: str = "",
    ):
        self.message = message
        self.response = response
        self.code = response.status
        self.url = response.url
        self.html = text

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.message!r}, {self.url!r}, {self.code!r})"
        )

    def __str__(self):
        return f"{self.message} ({self.url}, {self.code})"


class LoginFailedException(SpiderIOException):
    pass
