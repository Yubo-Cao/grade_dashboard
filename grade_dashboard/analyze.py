import re
from decimal import Decimal
from typing import Callable, Literal, ParamSpec, TypeVar

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_grade_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.is_for_grading == 1][~pd.isna(df.score)]


P = ParamSpec("P")
V = TypeVar("V")


def grade_df(fn: Callable[P, V]) -> Callable[P, V]:
    def wrapper(df, *args: P.args, **kwargs: P.kwargs) -> V:
        return fn(get_grade_df(df), *args, **kwargs)

    return wrapper


@grade_df
def get_total_score(df: pd.DataFrame) -> Decimal:
    total_weight = get_total_weight(df)
    total_score_by_type = df.groupby("measure_type").apply(
        lambda x: x.score.sum()
        / len(x)
        * x.weight.iloc[0]
        / total_weight  # hack: prevent decimal convert to float
    )
    total_score = total_score_by_type.sum()
    return total_score


@grade_df
def get_total_weight(df) -> Decimal:
    return df.drop_duplicates(subset="measure_type_id").weight.sum()


@grade_df
def get_score_by_type(df: pd.DataFrame) -> pd.Series:
    return df.groupby("measure_type").apply(lambda x: x.score.sum() / len(x))


@grade_df
def get_blame(df: pd.DataFrame) -> pd.Series:
    return (
        df.score
        / df.groupby("measure_type").score.transform("sum")
        * df.weight
        / get_total_weight(df)
    )


@grade_df
def get_contrib(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    count = df.groupby("measure_type_id").measure_type.count()
    df = df.join(count, on="measure_type_id", rsuffix="_count")
    return df.score / df.measure_type_count * df.weight / get_total_weight(df)


@grade_df
def plot_blame(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["blame"] = get_blame(df)
    return px.bar(
        df,
        x="blame",
        y="name",
        color="measure_type",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        orientation="h",
        title="Blame",
    )


@grade_df
def plot_score_by_type(df: pd.DataFrame) -> go.Figure:
    score_by_type = pd.DataFrame(get_score_by_type(df), columns=["score"])
    return px.bar(
        score_by_type.reset_index(),
        x="score",
        y="measure_type",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        orientation="h",
        title="Score by Type",
        color="measure_type",
    )


@grade_df
def plot_contrib(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["contrib"] = get_contrib(df)
    return px.bar(
        df,
        x="contrib",
        y="name",
        color="measure_type",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        orientation="h",
        title="Contrib",
    )


def extract_name(name: str):
    match = re.match(
        r"\([SQ]\d\)\s+[a-zA-Z-]+(?:,\s*\w+)\s*(.*?)\s*(?:\(\d+\))\s*(?:SEC:\d+\.\d+\-\d+)",
        name,
    )
    if not match:
        return "Unknown"
    return match.group(1).capitalize()


def plot_scores(
    data: list[dict],
    type: Literal["bar", "radar"] = "bar",
    normalize: bool = False,
    weighted: bool = False,
) -> go.Figure:
    df = pd.DataFrame(
        [
            {
                "name": extract_name(data["meta"]["name"]),
                "score": get_total_score(data["data"]),
                "ap": Decimal(data["meta"]["rigor_points"]),
            }
            for data in data
        ]
    )
    if weighted:
        df.score += df.ap
    mean = df.score.sum() / len(df)  # hack: prevent decimal convert to float
    title = f"Total Scores{' Normalized' if normalize else ''}—{mean:.2f}"
    if normalize:
        std = (df.score - mean).pow(2).sum() / len(df)
        df.score = (df.score - mean) / std
        df.score -= df.score.min() - 1
    if type == "bar":
        fig = px.bar(
            df,
            x="score",
            y="name",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            orientation="h",
            title=title,
        )
    else:
        fig = px.line_polar(
            df,
            r="score",
            theta="name",
            line_close=True,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=title,
        )
        fig.update_traces(fill="toself")
    return fig