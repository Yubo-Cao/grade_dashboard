from datetime import datetime

from decimal import Decimal
from typing import TypedDict, NotRequired


class MeasureType(TypedDict):
    """
    A measure type.
    """

    id: int
    name: str
    weight: Decimal
    drop_score: Decimal


class Comment(TypedDict):
    """
    A comment.
    """

    code: str
    content: str
    assignment_value: Decimal
    penalty_percent: Decimal


class GradeBookItem(TypedDict):
    """
    A grade book item.
    """

    id: int
    name: str
    points: Decimal
    max_points: Decimal
    score: Decimal
    max_score: Decimal
    due_date: datetime
    is_for_grade: bool
    is_hidden: bool
    is_missing: bool
    measure_type: MeasureType
    comment: Comment
    # the following are present if is_for_grade is True
    blame: NotRequired[
        Decimal
    ]  # the percentage of this assignment contributed to the grade
    contrib: NotRequired[
        Decimal
    ]  # the actual number of points contributed to the grade


class Course(TypedDict):
    """
    A course.
    """

    id: int
    name: str
    teacher: str
    grade: Decimal
    email: str
    period: str
