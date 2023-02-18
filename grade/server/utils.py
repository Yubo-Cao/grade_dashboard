import json
from decimal import Decimal
from typing import Callable, ParamSpec, TypeVar, Any

import pandas as pd
from aiohttp import web
from aiohttp.web_request import Request

from grade.spider import LoginFailedException, SpiderIOException

P = ParamSpec("P")
V = TypeVar("V")


def catch_common_exceptions(func: Callable[P, V]) -> Callable[P, V]:
    """
    Catch common exceptions and raise the appropriate HTTP exception

    Args:
        func: the function to wrap

    Returns:
        the wrapped function
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> V:
        try:
            return await func(*args, **kwargs)
        except LoginFailedException:
            raise web.HTTPUnauthorized(reason="Invalid username or password")
        except SpiderIOException:
            raise web.HTTPServiceUnavailable(reason="Spider failed to scrape")
        except Exception as e:
            raise web.HTTPInternalServerError(reason=str(e))

    return wrapper


def extract_auth(request: Request) -> tuple[str, str]:
    """
    Extract username and password from the request

    Args:
        request: the request that contains the username and password
        in body

    Returns:
        the username and password
    """

    username = request.headers.get("username")
    password = request.headers.get("password")
    if not username or not password:
        raise web.HTTPBadRequest(reason="Missing username or password")
    return username, password


async def extract_course(request):
    query = request.rel_url.query
    course_id = query.get("id")
    course_name = query.get("name")
    course_index = query.get("index")
    try:
        course_index = int(course_index)
    except (TypeError, ValueError):
        course_index = -1
    return course_id, course_index, course_name


class RobustEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, pd.DataFrame):
            return o.to_dict(orient="records")
        if isinstance(o, pd.Series):
            return o.to_dict()
        if isinstance(o, pd.Timestamp):
            return o.to_pydatetime().isoformat()
        return super(RobustEncoder, self).default(o)


def json_response(v: Any):
    return web.Response(
        text=json.dumps(v, cls=RobustEncoder),
        content_type="application/json",
    )
