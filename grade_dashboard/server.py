import json

import pandas as pd
from aiohttp import web
from decimal import Decimal

from .analyze import (
    get_blame,
    get_contrib,
    get_grade_df,
    get_score_by_type,
    get_total_score,
)
from .exception import LoginFailedException
from .parse import parse_class_data, parse_gradebook_items, parse_items
from .session_manager import manager
from .spider import courses, get_course_data, resolve_course


async def get_session(request):
    params = request.rel_url.query
    username = params.get("username")
    password = params.get("password")
    if not username or not password:
        raise web.HTTPBadRequest(reason="Missing username or password")
    try:
        s = await manager.get_session(username, password)
    except LoginFailedException:
        raise web.HTTPUnauthorized(reason="Invalid username or password")
    return s


async def handle_courses(request: web.Request):
    """Get all courses from the database"""

    s = await get_session(request)
    result = await courses(s)
    return json_response(result)


async def handle_course_data(request: web.Request):
    """Get a course data from the database"""

    params = request.rel_url.query
    type = params.get("type")
    s = await get_session(request)
    c = await get_course(request)
    class_data, items_data = await get_course_data(s, c)
    grade_book = parse_gradebook_items(class_data, items_data)
    grade_book_df, grade_book_meta = grade_book["data"], grade_book["meta"]
    class_data, items_data = parse_class_data(class_data), parse_items(items_data)
    match type:
        case "grade_book":
            result = grade_book
        case "blame":
            result = get_blame(grade_book_df)
        case "contrib":
            result = get_contrib(grade_book_df)
        case "items":
            result = get_grade_df(grade_book_df)
        case "score_by_type":
            result = get_score_by_type(grade_book_df)
        case "total_score":
            result = get_total_score(grade_book_df)
        case "meta":
            result = grade_book_meta
        case "comments":
            result = class_data["comments"]
        case "measure_types":
            result = class_data["measure_types"]
        case _:
            raise web.HTTPBadRequest(reason="Invalid type")
    return json_response(result)


async def handle_courses(request: web.Request):
    """Get all courses from the database"""

    s = await get_session(request)
    result = await courses(s)
    return json_response(result)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, pd.DataFrame):
            return o.to_dict(orient="records")
        if isinstance(o, pd.Series):
            return o.to_dict()
        if isinstance(o, pd.Timestamp):
            return o.to_pydatetime().isoformat()
        return super(DecimalEncoder, self).default(o)


def json_response(result):
    return web.Response(text=json.dumps(result, cls=DecimalEncoder))


async def get_course(request):
    params = request.rel_url.query
    id = params.get("id")
    name = params.get("name")
    index = params.get("index")
    if not any((id, name, index)):
        raise web.HTTPBadRequest(reason="Missing id, name, or index")
    if len(list(filter(bool, (id, name, index)))) > 1:
        raise web.HTTPBadRequest(reason="Too many parameters")
    s = await get_session(request)
    try:
        return await resolve_course(
            s,
            id or name or int(index),
            type="id" if id else "name" if name else "index",
        )
    except:
        raise web.HTTPNotFound(reason="Course not found")


async def handle_course(request: web.Request):
    return web.json_response(await get_course(request))


async def on_shutdown(app):
    await manager.cleanup()


def run():
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.add_routes(
        [
            web.get("/courses", handle_courses),
            web.get("/course", handle_course),
            web.get("/course/data", handle_course_data),
        ]
    )
    web.run_app(app, port=65535)
