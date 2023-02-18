import itertools as it
from datetime import datetime

from functools import cache
import pandas as pd

from grade_dashboard.spider import MeasureType, Comment, GradeBookItem
from grade_dashboard.utils import to_decimal, first, get, identifier


def parse_measure_types(class_data: dict[str, any]) -> list[MeasureType]:
    measure_types = class_data.get("measureTypes", [])
    return [
        MeasureType(
            id=mt.get("id"),
            name=mt.get("name"),
            weight=to_decimal(mt.get("weight")),
            drop_score=to_decimal(mt.get("dropScore")),
        )
        for mt in measure_types
    ]


def parse_comments(class_data: dict[str, any]) -> list[Comment]:
    comments = class_data.get("comments", [])
    return [
        Comment(
            code=c.get("commentCode"),
            content=c.get("comment"),
            assignment_value=to_decimal(c.get("assignmentValue")),
            penalty_percent=to_decimal(c.get("penaltyPct")),
        )
        for c in comments
    ]


def parse_grade_book_items(
    class_data: dict[str, any],
    items_data: dict[str, any],
) -> list[GradeBookItem]:
    items_df = pd.DataFrame(
        list(it.chain(*get(items_data, "responseData.data.*.items")))
    ).rename(identifier, axis="columns")
    assignments_df = pd.DataFrame(class_data.get("assignments", [])).rename(
        identifier, axis="columns"
    )
    df = pd.merge(
        items_df,
        assignments_df,
        left_on="item_id",
        right_on="grade_book_id",
        validate="one_to_one",
    )
    comments = parse_comments(class_data)

    @cache
    def get_comment_by_code(code) -> Comment:
        return first(filter(lambda c: c.get("code") == code, comments))

    measure_types = parse_measure_types(class_data)

    @cache
    def get_measure_type_by_id(id) -> MeasureType:
        return first(filter(lambda mt: mt.get("id") == id, measure_types))

    def transform(series: pd.Series) -> GradeBookItem:
        comment = get_comment_by_code(series.comment_code)
        if series.comment_text:
            comment["content"] = series.comment_text
        measure_type = get_measure_type_by_id(series.measure_type_id)
        return GradeBookItem(
            id=series.grade_book_id,
            name=series.title,
            points=to_decimal(series.points),
            max_points=to_decimal(series.max_value),
            score=to_decimal(series.score),
            max_score=to_decimal(series.max_score),
            due_date=datetime.fromisoformat(series.due_date_x),
            is_for_grade=series.is_for_grading,
            is_hidden=series.hide_in_portal,
            is_missing=series.is_grade_book_missing_mark,
            measure_type=measure_type,
            comment=comment,
        )

    return df.apply(transform, axis="columns").tolist()
