import asyncio

import aiohttp
from aiohttp import web

from .exception import LoginFailedException
from .parse import parse
from .session_manager import manager
from .spider import courses, fetch


async def get_courses(request: web.Request):
    """Get all courses from the database"""

    params = request.rel_url.query
    username = params.get("username")
    password = params.get("password")

    if not username or not password:
        raise web.HTTPBadRequest(reason="Missing username or password")

    s = await manager.get_session(username, password)
    try:
        result = await courses(s)
    except LoginFailedException:
        raise web.HTTPUnauthorized(reason="Invalid username or password")

    return web.json_response(result)


async def on_shutdown(app):
    await manager.cleanup()


def run():
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.add_routes([web.get("/courses", get_courses)])
    web.run_app(app)
