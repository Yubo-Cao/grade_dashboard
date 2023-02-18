from typing import TypeVar, ParamSpec, overload, Protocol, Any, cast
from collections.abc import Callable, Awaitable
import asyncio


P = ParamSpec("P")
V = TypeVar("V", covariant=True)
PLACE_HOLDER: Any = object()


class SyncCache(Protocol[P, V]):
    def __init__(self, size: int, fn: Callable[P, V]) -> None:
        ...

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        ...

    def clear(self) -> None:
        ...


class SingleSyncCache(SyncCache[P, V]):
    def __init__(self, size: int, fn: Callable[P, V]) -> None:
        if size != 1:
            raise ValueError("SingleSyncCache only supports size=1")
        self.fn = fn
        self.result: V = PLACE_HOLDER

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        if self.result is PLACE_HOLDER:
            self.result = self.fn(*args, **kwargs)
        return self.result

    def clear(self) -> None:
        self.result = PLACE_HOLDER


class MultiSyncCache(SyncCache[P, V]):
    def __init__(self, size: int, fn: Callable[P, V]) -> None:
        if size <= 1:
            raise ValueError("MultiSyncCache only supports size > 1")
        self.fn = fn
        self.size = size
        self.result: dict[tuple[Any, ...], V] = {}

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        key = (args, tuple(kwargs.items()))
        r = self.result.get(key, PLACE_HOLDER)
        if r is PLACE_HOLDER:
            r = self.fn(*args, **kwargs)
            self.result[key] = r
            if len(self.result) > self.size:
                self.result.popitem()
        return r

    def clear(self) -> None:
        self.result = {}


class AsyncCache(Protocol[P, V]):
    def __init__(self, size: int, fn: Callable[P, V]) -> None:
        ...

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        ...

    def clear(self) -> None:
        ...


class SingleAsyncCache(AsyncCache[P, V]):
    def __init__(self, size: int, fn: Callable[P, Awaitable[V]]) -> None:
        if size != 1:
            raise ValueError("SingleAsyncCache only supports size=1")
        self.fn = fn
        self.result: V = PLACE_HOLDER

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        if self.result is PLACE_HOLDER:
            self.result = await self.fn(*args, **kwargs)
        return self.result

    def clear(self) -> None:
        self.result = PLACE_HOLDER


class MultiAsyncCache(AsyncCache[P, V]):
    def __init__(self, size: int, fn: Callable[P, Awaitable[V]]) -> None:
        if size <= 1:
            raise ValueError("MultiAsyncCache only supports size > 1")
        self.fn = fn
        self.size = size
        self.result: dict[tuple[Any, ...], V] = {}

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        key = (args, tuple(kwargs.items()))
        r = self.result.get(key, PLACE_HOLDER)
        if r is PLACE_HOLDER:
            r = await self.fn(*args, **kwargs)
            self.result[key] = r
            if len(self.result) > self.size:
                self.result.popitem()
        return r

    def clear(self) -> None:
        self.result = {}


@overload
def cached(
    size: int, /
) -> Callable[[Callable[P, V]], SyncCache[P, V] | AsyncCache[P, V]]:
    ...


@overload
def cached(fn: Callable[P, V], /) -> SyncCache[P, V] | AsyncCache[P, V]:
    ...


def cached(
    size: Callable[P, V] | int,
) -> (
    Callable[[Callable[P, V]], SyncCache[P, V] | AsyncCache[P, V]]
    | SyncCache[P, V]
    | AsyncCache[P, V]
):
    if callable(size):
        return cached(1)(size)

    def config(fn: Callable[P, V]) -> SyncCache[P, V] | AsyncCache[P, V]:
        nonlocal size
        size = cast(int, size)
        if asyncio.iscoroutinefunction(fn):
            if size == 1:
                return SingleAsyncCache(size, fn)
            else:
                return MultiAsyncCache(size, fn)
        else:
            if size == 1:
                return SingleSyncCache(size, fn)
            else:
                return MultiSyncCache(size, fn)

    return config
