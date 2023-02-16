import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar, cast

from .log import LOGGER

P = ParamSpec("P")
V = TypeVar("V", covariant=True)


def retry_async(
    fn: Callable[P, Awaitable[V]] | None = None,
    *,
    max_retries: int = 3,
    delay: float = 0.1,
    deps: list[Any] = [],
) -> Callable[P, Awaitable[V]] | Callable[
    [Callable[P, Awaitable[V]]], Callable[P, Awaitable[V]]
]:
    if fn is None:

        def wrapper(fn: Callable[P, Awaitable[V]]) -> Callable[P, Awaitable[V]]:
            return cast(
                Callable[P, Awaitable[V]],
                retry_async(fn, max_retries=max_retries, delay=delay),
            )

        return wrapper

    f = cast(Callable[P, Awaitable[V]], fn)

    async def decorator(*args: P.args, **kwargs: P.kwargs) -> V:
        for i in range(max_retries):
            try:
                return await f(*args, **kwargs)
            except Exception as e:
                if i == max_retries - 1:
                    LOGGER.exception(e)
                    raise
                LOGGER.info(f"Retrying {f.__name__} in {delay} seconds")
                if (clear := getattr(f, "clear", None)) is not None:  # invalidate cache
                    clear()
                for dep in deps:
                    if (clear := getattr(dep, "clear", None)) is not None:
                        clear()
                await asyncio.sleep(delay)
        return await f(*args, **kwargs)

    return decorator


def retry_sync(
    fn: Callable[P, V] | None = None,
    *,
    max_retries: int = 3,
    delay: float = 0.1,
    deps: list[Any] = [],
) -> Callable[P, V] | Callable[[Callable[P, V]], Callable[P, V]]:
    if fn is None:

        def wrapper(fn: Callable[P, V]) -> Callable[P, V]:
            return cast(
                Callable[P, V],
                retry_sync(fn, max_retries=max_retries, delay=delay),
            )

        return wrapper

    f = cast(Callable[P, V], fn)

    def decorator(*args: P.args, **kwargs: P.kwargs) -> V:
        for i in range(max_retries):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if i == max_retries - 1:
                    LOGGER.exception(e)
                    raise
                if (clear := getattr(f, "clear", None)) is not None:  # invalidate cache
                    clear()
                for dep in deps:
                    if (clear := getattr(dep, "clear", None)) is not None:
                        clear()
                LOGGER.info(f"Retrying {f.__name__} in {delay} seconds")
                time.sleep(delay)
        return f(*args, **kwargs)

    return decorator


def retry(
    fn: Callable[P, V] | None = None,
    *,
    max_retries: int = 3,
    delay: float = 0.1,
    deps: list[Any] = [],
) -> (
    Callable[P, V]
    | Callable[[Callable[P, V]], Callable[P, V]]
    | Callable[P, Awaitable[V]]
    | Callable[[Callable[P, Awaitable[V]]], Callable[P, Awaitable[V]]]
):
    if asyncio.iscoroutinefunction(fn):
        return retry_async(fn, max_retries=max_retries, delay=delay, deps=deps)
    else:
        return retry_sync(fn, max_retries=max_retries, delay=delay, deps=deps)
