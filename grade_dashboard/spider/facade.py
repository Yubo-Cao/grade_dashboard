from decimal import Decimal
from typing import TypedDict
from session_manager import manager
from .spider import courses
import re


class Course(TypedDict):
    id: int
    name: str
    teacher: str
    grade: Decimal
    email: str
    period: str


async def get_courses(username: str, password: str) -> list[Course]:
    """
    Get the courses for the specified user.

    :param username: The username of the user.
    :param password: The password of the user.

    :return: A list of courses.
    """

    s = await manager.get_session(username, password)
    cs = await courses(s)
    course_re = re.compile(r"(?P<period>\d+):\s*(?P<name>.+?)\s*$")
    matches = [course_re.match(c) for c in cs]
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
