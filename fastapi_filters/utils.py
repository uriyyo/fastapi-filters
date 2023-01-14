from functools import wraps
from typing import Awaitable, Callable, TypeVar, Sequence, Any, Union

from pydantic.utils import lenient_issubclass
from pydantic.typing import is_union, get_args, is_none_type, get_origin
from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def async_safe(f: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(*args, **kwargs)

    return wrapper


def is_optional(tp: Any) -> bool:
    return is_union(get_origin(tp)) and any(is_none_type(arg) for arg in get_args(tp))


def is_seq(tp: Any) -> bool:
    return lenient_issubclass(get_origin(tp), Sequence)


def unwrap_type(tp: Any) -> Any:
    if is_optional(tp):
        return Union[tuple(arg for arg in get_args(tp) if not is_none_type(arg))]
    if is_seq(tp):
        return Union[tuple(get_args(tp))]

    return tp


__all__ = [
    "async_safe",
    "is_seq",
    "is_optional",
    "unwrap_type",
]
