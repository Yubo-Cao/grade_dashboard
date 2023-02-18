import itertools as it
from typing import get_type_hints

import pandas as pd
from pandas import DataFrame

from grade.spider.model import *
from grade.utils import to_decimal
from grade.utils.df import explode, condense


def grade_book_items_to_df(grade_book_items: list[GradeBookItem]) -> pd.DataFrame:
    """
    Convert a list of grade book items to a DataFrame.

    Args:
        grade_book_items: the grade book items

    Returns:
        the DataFrame
    """

    df = DataFrame(grade_book_items)
    df = explode(df, "comment", Comment)
    df = explode(df, "measure_type", MeasureType)
    return df.set_index("id")


def df_to_grade_book_items(df: pd.DataFrame) -> list[GradeBookItem]:
    """
    Convert a DataFrame to a list of grade book items.

    Args:
        df: the DataFrame

    Returns:
        the grade book items
    """

    df = condense(df, "comment", Comment)
    df = condense(df, "measure_type", MeasureType)
    return df.to_dict(orient="records")


def _calculate_adjusted_score(
    grade_book_items: pd.DataFrame,
    inplace: bool = False,
) -> list[GradeBookItem["id"], Decimal] | None:
    """
    Calculate the adjusted score of the grade book items.
    """
    df = grade_book_items
    df = df[df["is_for_grade"] & ~df["is_hidden"]]
    df.loc[df["is_missing"], "points"] = to_decimal(0)
    points = df["comment_assignment_value"].fillna(df["points"]).fillna(to_decimal(0))
    score = points / df["max_points"] * df["max_score"]
    score = score * (
        1 - (df["comment_penalty_percent"] / to_decimal(100)).fillna(to_decimal(0))
    )
    score = score - df["measure_type_drop_score"].fillna(to_decimal(0))
    score = score.clip(upper=df["max_score"])

    if inplace:
        df["adjusted_score"] = score
    else:
        return score


def _ensure_adjusted_score(grade_book_items: pd.DataFrame) -> pd.DataFrame:
    if "adjusted_score" not in grade_book_items.columns:
        grade_book_items = grade_book_items.copy()
        _calculate_adjusted_score(grade_book_items, inplace=True)
    return grade_book_items


def calculate_score(grade_book_items: pd.DataFrame) -> Decimal:
    """
    Calculate the final score of the grade book items.
    """

    grade_book_items = _ensure_adjusted_score(grade_book_items)
    df = grade_book_items.groupby("measure_type_id")
    means = df["adjusted_score"].sum() / df["adjusted_score"].count()
    weights = df["measure_type_weight"].sum()
    return ((means * weights) / weights.sum()).sum()


def calculate_score_by_measure_type(
    grade_book_items: pd.DataFrame,
) -> dict[MeasureType["id"], Decimal]:
    """
    Calculate the score of each measure type.
    """

    grade_book_items = _ensure_adjusted_score(grade_book_items)
    df = grade_book_items.groupby("measure_type_id")
    means = df["adjusted_score"].sum() / df["adjusted_score"].count()
    return means.to_dict()


def calculate_blame(
    grade_book_items: pd.DataFrame,
) -> dict[GradeBookItem["id"], Decimal]:
    """
    Calculate the blame of each grade book item.

    Blame is a number between 0 and 1, where 0 means the grade book item has no
    impact on the final score, and 1 means the grade book item has the maximum
    impact on the final score. All blame values sum up to 1.
    """

    total_weight = grade_book_items.drop_duplicates(
        "measure_type_id"
    ).measure_type_weight.sum()
    bdf = grade_book_items[
        [
            "id",
            "is_missing",
            "is_hidden",
            "is_for_grade",
            "max_score",
            "measure_type_weight",
            "measure_type_id",
            "measure_type_drop_score",
            "comment_penalty_percent",
        ]
    ].set_index("id")
    return (
        bdf.assign(blame=to_decimal(1))
        .pipe(
            lambda df: df[~(df["is_hidden"] | df["is_missing"] | ~df["is_for_grade"])]
        )
        .assign(
            blame=lambda df: df["blame"]
                             * (1 - df["comment_penalty_percent"].fillna(to_decimal(0)) / 100)
        )
        .groupby("measure_type_id", group_keys=False)
        .apply(
            lambda g: g.assign(
                blame=g["blame"]
                      / g["blame"].count()
                      * (g["measure_type_weight"] / total_weight)
            )
        )
        .assign(
            blame=lambda df: df["blame"]
                             - df["measure_type_drop_score"].fillna(to_decimal(0))
                             / df["max_score"].fillna(to_decimal(100))
        )["blame"]
        .to_dict()
    )


def calculate_contrib(
    grade_book_items: pd.DataFrame,
) -> dict[GradeBookItem["id"], Decimal]:
    """
    Calculate the contribution of each grade book item.

    Contribution is a number between 0 and 100, where 0 means the grade book item
    contributed nothing to the final score, and 100 means the grade book item
    contributed the maximum possible score to the final score.
    """

    grade_book_items = _ensure_adjusted_score(grade_book_items)
    total_weight = grade_book_items.drop_duplicates(
        "measure_type_id"
    ).measure_type_weight.sum()
    return (
        grade_book_items.groupby("measure_type_id", group_keys=False)
        .apply(lambda g: g.assign(count=g["adjusted_score"].count()))
        .apply(
            lambda g: g.adjusted_score
                      * g.measure_type_weight
                      / total_weight
                      / g["count"],
            axis=1,
        )
        .to_dict()
    )


def calculate_what_if(
    grade_book_items: list[GradeBookItem],
    existing_items: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return a new DataFrame with updated or appended grade book items.

    For each grade book item in the input list, update the corresponding item in the
    existing DataFrame if it has the same ID, or append it to the DataFrame if it has
    a different ID.
    """

    new_items = grade_book_items_to_df(grade_book_items)

    matching_ids = new_items.index.isin(existing_items.index)
    updated_items = new_items[matching_ids]
    appended_items = new_items[~matching_ids]

    existing_items.loc[updated_items.index] = updated_items
    all_items = pd.concat([existing_items, appended_items])

    columns = set(
        it.chain(
            get_type_hints(GradeBookItem).keys(),
            get_type_hints(MeasureType).keys(),
            get_type_hints(Comment).keys(),
        )
    )
    return all_items[[c for c in all_items.columns if c in columns]]
