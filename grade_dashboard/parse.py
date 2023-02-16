from decimal import Decimal
from typing import Any

import pandas as pd

from .utils import flatten, identifier


def parse_class_data(cd: dict[str, any]) -> dict[str, dict | pd.DataFrame]:
    """Parse class data from the response of the gradebook API.

    Args:
        cd (dict[str, any]): class data dictionary

    Returns:
        dict[str, dict | pd.DataFrame]: parsed class data
        - meta: class metadata
        - measure_types: measure types
        - assignments: assignments
        - comments: comments
    """
    meta = dict(
        class_id=cd.get("classId"),
        name=cd.get("className"),
        rigor_points=cd.get("rigorPoints"),
    )
    # measure types
    mt_df = (
        pd.DataFrame(cd.get("measureTypes"))
        .set_index("id")
        .rename(identifier, axis="columns")[["name", "drop_scores", "weight"]]
    )
    mt_df = mt_df[mt_df.weight > 0]
    # assignments
    as_df = (
        pd.DataFrame(cd.get("assignments"))
        .rename(identifier, axis="columns")
        .set_index("grade_book_id")
    )[
        [
            "measure_type_id",
            "score",
            "max_value",
            "max_score",
            "due_date",
            "is_for_grading",
            "comment_code",
        ]
    ]
    as_df.due_date = pd.to_datetime(as_df.due_date)
    cols = ["score", "max_score", "max_value"]
    as_df[cols] = as_df[cols].astype(float)
    # comments
    co_df = (
        pd.DataFrame(cd.get("comments"))
        .rename(identifier, axis="columns")
        .set_index("comment_code")[["comment", "assignment_value", "penalty_pct"]]
    )
    co_df.assignment_value = co_df.assignment_value.astype(float)
    co_df.penalty_pct = co_df.penalty_pct.astype(float)
    return dict(meta=meta, measure_types=mt_df, assignments=as_df, comments=co_df)


def parse_items(items: dict[str, Any]) -> pd.DataFrame:
    """Parse items from the response of the gradebook API.

    Args:
        items (dict[str, Any]): items dictionary

    Returns:
        pd.DataFrame: parsed items
    """
    items = items["responseData"]["data"]
    df = pd.DataFrame(flatten(e.get("items", []) for e in items)).rename(
        identifier,
        axis="columns",
    )[
        ["item_id", "title", "assignment_type", "due_date", "points"]
    ]  # grade_mark
    df.points = pd.to_numeric(df.points, errors="coerce").astype(float)
    df.due_date = pd.to_datetime(df.due_date)
    df.set_index("item_id", inplace=True)
    return df


def parse_gradebook_items(
    class_data: dict[str, Any],
    items: dict[str, Any],
) -> dict[str, pd.DataFrame | dict[str, str]]:
    """Parse gradebook items from the response of the gradebook API.

    Args:
        class_data (dict[str, Any]): the class data dictionary
        items (dict[str, Any]): the items dictionary

    Returns:
        dict[str, pd.DataFrame | dict[str, str]]: parsed gradebook items
    """
    class_data = parse_class_data(class_data)
    items = parse_items(items)
    df: pd.DataFrame = (
        class_data["measure_types"]
        .merge(class_data["assignments"], left_index=True, right_on="measure_type_id")
        .join(items["title"])
        .join(class_data["comments"], on="comment_code", how="left")
    )
    df = df.rename(
        columns={
            "name": "measure_type",
            "title": "name",
            "assignment_value": "comment_assignment_value",
        }
    ).apply(
        lambda x: x.apply(lambda e: Decimal(e))
        if pd.api.types.is_numeric_dtype(x)
        else x,
        axis="rows",
    )
    adjusted_score = df.comment_assignment_value.fillna(
        df.score
    ) - df.drop_scores.fillna(Decimal(0.0))
    adjusted_score = (
        adjusted_score
        / df.max_score.fillna(Decimal(100.0))
        * 100
        * (1 - df.penalty_pct.fillna(Decimal(0.0)) / 100)
    )
    df.score = adjusted_score
    return {
        "meta": class_data["meta"],
        "data": df.drop(
            columns=[
                "drop_scores",
                "max_value",
                "max_score",
                "comment_assignment_value",
            ]
        )[~pd.isna(df.name)],
    }


def parse_courses_data(
    result: list[tuple[dict, dict]]
) -> list[dict[str, dict[str, str] | pd.DataFrame]]:
    return [parse_gradebook_items(*e) for e in result]
