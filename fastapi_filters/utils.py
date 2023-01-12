from functools import wraps
from typing import Awaitable, Callable, TypeVar, get_origin, List

from pydantic.utils import lenient_issubclass
from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def async_safe(f: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(*args, **kwargs)

    return wrapper


def is_list(tp: type) -> bool:
    return lenient_issubclass(get_origin(tp), List)


__all__ = [
    "async_safe",
    "is_list",
]
