import asyncio
import json
import threading
from decimal import Decimal
from io import StringIO
from typing import Any

import pandas as pd
from aiohttp import web
from plotly import graph_objects as go

from .analyze import (
    get_blame,
    get_contrib,
    get_score_by_type,
    get_total_score,
    plot_blame,
    plot_contrib,
    plot_score_by_type,
    plot_scores,
)
from .spider.exception import LoginFailedException
from grade.spider.parse import (
    parse_class_data,
    parse_courses_data,
    parse_grade_book_items,
    parse_items,
)
from .spider.session_manager import manager
from .spider.spider import courses, get_course_data, get_courses_data, resolve_course

routes = web.RouteTableDef()


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


@routes.get("/courses")
async def handle_courses(request: web.Request):
    """Get all courses from the database"""

    s = await get_session(request)
    result = await courses(s)
    return json_response(result)


@routes.get("/course/data")
async def handle_course_data(request: web.Request):
    """Get a course data from the database"""

    params = request.rel_url.query
    type = params.get("type")
    s = await get_session(request)
    c = await get_course(request)
    class_data, items_data = await get_course_data(s, c)
    grade_book = parse_grade_book_items(class_data, items_data)
    grade_book_df, grade_book_meta = grade_book["data"], grade_book["meta"]
    if type == "raw":
        result = {
            "class_data": class_data,
            "items_data": items_data,
        }
    class_data, items_data = parse_class_data(class_data), parse_items(items_data)
    match type:
        case "raw":
            pass
        case "grade_book":
            result = grade_book
        case "blame":
            result = get_blame(grade_book_df)
        case "contrib":
            result = get_contrib(grade_book_df)
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


def json_response(result: Any):
    return web.Response(
        text=json.dumps(result, cls=DecimalEncoder),
        content_type="application/json",
    )


async def get_course(request: web.Request):
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
            query=id or name or int(index),
            query_type="id" if id else "name" if name else "index",
        )
    except:
        raise web.HTTPNotFound(reason="Course not found")


@routes.get("/course")
async def handle_course(request: web.Request):
    return web.json_response(await get_course(request))


async def on_shutdown(app):
    await manager.cleanup()


def fig_to_html(fig: go.Figure) -> str:
    buf = StringIO()
    fig.write_html(buf)
    return buf.getvalue()


@routes.get("/course/plot")
async def handle_course_plot(request: web.Request):
    c = await get_course(request)
    grade_book_items = parse_grade_book_items(
        *(await get_course_data(await get_session(request), c))
    )
    grade_book_df = grade_book_items["data"]
    params = request.rel_url.query
    type = params.get("type")
    match type:
        case "blame":
            result = fig_to_html(plot_blame(grade_book_df))
        case "contrib":
            result = fig_to_html(plot_contrib(grade_book_df))
        case "score_by_type":
            result = fig_to_html(plot_score_by_type(grade_book_df))
        case _:
            raise web.HTTPBadRequest(reason="Invalid type")
    return web.Response(text=result, content_type="text/html")


@routes.get("/courses/plot")
async def handle_courses_plot(request: web.Request):
    params = request.rel_url.query
    type = params.get("type", "bar")
    normalize = params.get("normalize", "false").lower() == "true"
    weighted = params.get("weighted", "false").lower() == "true"
    data = parse_courses_data(await get_courses_data(await get_session(request)))
    return web.Response(
        text=fig_to_html(
            plot_scores(
                data,
                type=type,
                normalize=normalize,
                weighted=weighted,
            )
        ),
        content_type="text/html",
    )


def run(event: asyncio.Event | threading.Event):
    app = web.Application()

    async def check_for_shutdown(app):
        while True:
            await asyncio.sleep(1)
            if event.is_set():
                await app.shutdown()

    async def bootstrap(app):
        asyncio.create_task(check_for_shutdown(app))

    app.on_startup.append(bootstrap)
    app.on_shutdown.append(on_shutdown)
    app.add_routes(routes)
    web.run_app(app, port=65535)
