from typing import get_type_hints

import pandas as pd
from pandas import DataFrame


def explode(df: pd.DataFrame, col: str, type: type) -> DataFrame:
    return df.assign(
        **{
            f"{col}_{k}": df[col].apply(lambda dct: (dct or {}).get(k))
            for k in list(get_type_hints(type).keys())
        }
    ).drop(col, axis=1)


def condense(df: pd.DataFrame, col: str, type: type) -> DataFrame:
    return df.assign(
        **{
            col: df.apply(
                lambda row: {
                    k: row[f"{col}_{k}"] for k in list(get_type_hints(type).keys())
                },
                axis=1,
            )
        }
    ).drop([f"{col}_{k}" for k in list(get_type_hints(type).keys())], axis=1)
