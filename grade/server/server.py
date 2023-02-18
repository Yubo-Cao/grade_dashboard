import asyncio
import threading

from aiohttp import web
from aiohttp.web import Request, Response, RouteTableDef

from grade.spider import get_courses, get_course, get_grade_book_items, manager
from .utils import extract_auth, catch_common_exceptions, extract_course, json_response

routes = RouteTableDef()


@routes.get("/courses")
@catch_common_exceptions
async def handle_courses(request: Request) -> Response:
    """
    Get all courses from the database

    Args:
        request: a request object with the username and password

    Returns:
        a response object with the courses
    """

    username, password = extract_auth(request)
    courses = await get_courses(username, password)
    return json_response(courses)


@routes.get("/course/data")
@catch_common_exceptions
async def handle_course_data(request: Request) -> Response:
    """
    Get a course data from the database

    Args:
        request: a request object with the username and password

    Returns:
        a response object with the course data
    """

    username, password = extract_auth(request)
    query = request.rel_url.query
    course_id = query.get("id")
    course_name = query.get("name")
    course_index = query.get("index")
    try:
        course_index = int(course_index)
    except (TypeError, ValueError):
        course_index = -1
    course = await get_course(username, password, course_id=course_id, course_name=course_name,
                              course_index=course_index)
    return json_response(course)


@routes.get("/course/grade_book_items")
@catch_common_exceptions
async def handle_grade_book_items(request: Request) -> Response:
    """
    Get a course data from the database

    Args:
        request: a request object with the username and password

    Returns:
        a response object with the course data
    """

    username, password = extract_auth(request)
    course_id, course_index, course_name = await extract_course(request)
    grade_book_items = await get_grade_book_items(username, password, course_id=course_id,
                                                  course_name=course_name, course_index=course_index)
    return json_response(grade_book_items)


def run(event: asyncio.Event | threading.Event, port: int = 65535):
    """
    Run the server

    Args:
        event: the event to check for shutdown
        port: the port to run the server on

    Returns:
        None
    """

    app = web.Application()

    async def bootstrap(this_app: web.Application) -> None:
        async def check_for_shutdown() -> None:
            while True:
                await asyncio.sleep(1)
                if event.is_set():
                    await this_app.shutdown()

        asyncio.create_task(check_for_shutdown())

    async def cleanup(_: web.Application) -> None:
        await manager.cleanup()

    app.on_startup.append(bootstrap)
    app.on_shutdown.append(cleanup)
    app.add_routes(routes)

    web.run_app(app, port=port)
