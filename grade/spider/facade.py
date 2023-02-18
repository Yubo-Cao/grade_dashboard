import re

from .model import GradeBookItem, Course
from .parse import parse_grade_book_items
from .session_manager import manager
from .spider import courses, get_course_data, resolve_course


async def get_courses(username: str, password: str) -> list[Course]:
    """
    Get the courses for the specified user.

    Args:
        username: the username of the user
        password: the password of the user

    Returns:
        the courses
    """

    s = await manager.get_session(username, password)
    cs = await courses(s)
    course_re = re.compile(r"(?P<period>\d+):\s*(?P<name>.+?)\s*$")
    matches = [course_re.match(c.get("course")) for c in cs]
    return [
        Course(
            id=c.get("id"),
            name=m.group("name"),
            teacher=c.get("teacher"),
            grade=c.get("grade"),
            email=c.get("email"),
            period=m.group("period"),
        )
        for c, m in zip(cs, matches)
        if m
    ]


async def get_course(
    username: str,
    password: str,
    course_id: int | str = -1,
    course_name: str = "",
    course_index: int = -1,
) -> Course:
    """
    Get the course for the specified user.

    Args:
        username: the username of the user
        password: the password of the user
        and one of the following:
            course_id: the id of the course
            course_name: the name of the course
            course_index: the index of the course in the list of courses

    Returns:
        the course
    """

    cs = await get_courses(username, password)
    if course_id != -1:
        return next(c for c in cs if str(c.get("id")) == str(course_id))
    if course_name:
        return next(c for c in cs if c.get("name") == course_name)
    if course_index != -1:
        return cs[course_index]
    raise ValueError("No course specified.")


async def get_grade_book_items(
    username: str,
    password: str,
    course_id: int | str = -1,
    course_name: str = "",
    course_index: int = -1,
) -> list[GradeBookItem]:
    """
    Get the grade book items for the specified user and course.

    Args:
        username: the username of the user
        password: the password of the user
        and one of the following:
            course_id: the id of the course
            course_name: the name of the course
            course_index: the index of the course in the list of courses

    Returns:
        the grade book items
    """

    course = await get_course(username, password, course_id, course_name, course_index)
    session = await manager.get_session(username, password)
    class_data, items_data = await get_course_data(
        session,
        await resolve_course(session, query=course["id"], query_type="id"),
    )
    return parse_grade_book_items(
        class_data,
        items_data,
    )
