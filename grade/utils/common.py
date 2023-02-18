import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, cast, TypeVar
from typing import Callable
from decimal import Decimal, DecimalException

from .constants import DECIMAL_CONTEXT

E = TypeVar("E")
D = TypeVar("D")


def first(iterable: Iterable[E], default: E | None = None) -> E | None:
    return next(iter(iterable), cast(E, default))


def identifier(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]", "_", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def find(
    iterable: dict[str, E] | list[tuple[str, E]],
    s: str,
    default: E | None = None,
) -> E | None:
    if isinstance(iterable, dict):
        return iterable.get(s)
    return first((v for k, v in iterable if k == s), default)


def to_matched(
    s: str,
    start: int = 0,
    end: int = -1,
    patterns: tuple[tuple[str, str]] = (
        ("(", ")"),
        ("[", "]"),
        ("{", "}"),
    ),
) -> int:
    if end == -1:
        end = len(s)
    start_chars, end_chars = (set(x) for x in zip(*patterns, strict=True))
    end2start = {v: k for k, v in patterns}

    stk = []
    if s[start] not in start_chars:
        raise ValueError(f"Expected start char, got {s[start]}")
    stk.append(s[start])
    start += 1
    while start < end:
        if s[start] in start_chars:
            stk.append(s[start])
        elif s[start] in end_chars:
            if stk[-1] != end2start[s[start]]:
                raise ValueError(f"Expected {stk[-1]}, got {s[start]}")
            stk.pop()
            if not stk:
                return start
        start += 1
    if stk:
        raise ValueError(f"Expected {stk[-1]}, got EOF")
    return end


def get_var(var_name: str, script: str) -> Any:
    match = re.search(re.escape(var_name) + r"\s*=\s*", script)
    if not match:
        raise ValueError(f"Cannot find {var_name}")
    st = match.end()
    ed = to_matched(script, st)
    data = json.loads(script[st : ed + 1])
    return data


def extract_dict(
    dct: dict[str, Any] | list[tuple[str, Any]],
    fields: list[str],
    tfms: Callable[[str], str] = lambda x: x,
    default: E | None = None,
) -> dict[str, Any]:
    result = {}
    for field in fields:
        result[tfms(field)] = find(dct, field, default)
    return result


def chunked(iterable: list[E], n: int) -> Iterable[list[E]]:
    return (iterable[i : i + n] for i in range(0, len(iterable), n))


def flatten(iterable: Iterable[Iterable[E]]) -> Iterable[E]:
    return (item for sublist in iterable for item in sublist)


FT = TypeVar("FT")
ST = TypeVar("ST")
TT = TypeVar("TT")


def compose(f: Callable[[FT], ST], g: Callable[[ST], TT]) -> Callable[[FT], TT]:
    return lambda x: g(f(x))


def strip(
    s: str | Iterable[str] | Mapping[str, str]
) -> str | Iterable[str] | Mapping[str, str]:
    if isinstance(s, str):
        return s.strip()
    if isinstance(s, Iterable):
        return [strip(x) for x in s]
    if isinstance(s, Mapping):
        return {k: strip(v) for k, v in s.items()}
    raise TypeError(f"Cannot strip {s}")


def get(dct: dict[str, Any], key: str, default: D | None = None) -> D | None:
    """
    Get value from dict by key.

    Args:
        dct: the dict to get value from
        key: the key to get value. Use "." to access nested dict and "*" to aggregate values.
        default: the default value to return if key not found

    Returns:
        the value of the key or default value if key not found
    """
    result: Any = dct
    keys = key.split(".")
    for i in range(len(keys)):
        key = keys[i]
        if key == "*":
            return [
                get(dct, ".".join(keys[i + 1 :]), default)
                for dct in (result.values() if isinstance(result, dict) else result)
            ]
        result = getattr(result, "get", lambda *args, **kwargs: None)(key)
        if result is None:
            return default
    return result


def rename(dct: dict, mapper: Callable[[str], str] = None, **kwargs) -> dict:
    """
    Rename keys in a dict. If both mapper and kwargs are provided, mapper will be applied first.

    Args:
        dct: the dict to rename keys
        mapper: the function to map keys
        **kwargs: or, you can use keyword arguments to rename keys

    Returns:
        the dict with renamed keys
    """

    result = {kwargs.get(k, k): v for k, v in dct.items()}
    if mapper:
        result = {mapper(k): v for k, v in result.items()}
    return result


def to_decimal(v) -> Decimal:
    """
    Convert value to Decimal, ignore all exceptions and return NaN if failed.

    Args:
        v: a value to convert

    Returns:
        the Decimal value
    """
    try:
        return Decimal(v, DECIMAL_CONTEXT)
    except (DecimalException, TypeError):
        return Decimal("NaN", DECIMAL_CONTEXT)
