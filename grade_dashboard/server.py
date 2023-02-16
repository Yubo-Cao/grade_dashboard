import asyncio
import aiohttp
from aiohttp import web

from .parse import parse
from .spider import fetch


async def get_courses(request: web.Request):
    """Get all courses from the database"""

    params = request.rel_url.query
    username = params.get("username")
    password = params.get("password")

    if not username or not password:
        return web.json_response({"error": "Missing username or password"})
