import types
from collections.abc import Awaitable, Callable, Container, Iterable, Sequence
from functools import wraps
from typing import (
    Annotated,
    Any,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from fastapi.dependencies.utils import lenient_issubclass
from pydantic.fields import FieldInfo
from typing_extensions import ParamSpec

try:
    from fastapi._compat.shared import field_annotation_is_complex
except ImportError:
    from fastapi._compat import field_annotation_is_complex  # type: ignore[attr-defined,no-redef]

P = ParamSpec("P")
T = TypeVar("T")


def async_safe(f: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(*args, **kwargs)

    return wrapper


def is_none_type(tp: Any) -> bool:
    return tp in (type(None), None, None)


def is_union(tp: Any) -> bool:
    return tp in (Union, types.UnionType) or get_origin(tp) in (Union, types.UnionType)


def is_optional(tp: Any) -> bool:
    return is_union(get_origin(tp)) and any(is_none_type(arg) for arg in get_args(tp))


def is_seq(tp: Any) -> bool:
    return not lenient_issubclass(tp, (str, bytes)) and (
        lenient_issubclass(tp, Sequence) or lenient_issubclass(get_origin(tp), Sequence)
    )


def _create_union(*args: Any, exclude_none: bool = True) -> Any:
    args = tuple(arg for arg in args if arg is not ...)
    if exclude_none:
        args = tuple(arg for arg in args if not is_none_type(arg))

    return Union[args]


def unwrap_optional_type(tp: Any) -> Any:
    if not is_optional(tp):
        raise TypeError(f"Expected optional type, got {tp}")

    return _create_union(*get_args(tp), exclude_none=True)


def unwrap_seq_type(tp: Any) -> Any:
    if not is_seq(tp):
        raise TypeError(f"Expected sequence type, got {tp}")

    return _create_union(*(get_args(tp) or (Any,)), exclude_none=False)


def unwrap_type(tp: Any) -> Any:
    if is_optional(tp):
        return unwrap_optional_type(tp)
    if is_seq(tp):
        return unwrap_seq_type(tp)

    return tp


def unwrap_annotated(tp: Any) -> Any:
    if get_origin(tp) is Annotated:
        return tp.__origin__

    return tp


def fields_include_exclude(
    fields: Iterable[str],
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
) -> Callable[[str], bool]:
    if include is None:
        include = {*fields}
    if exclude is None:
        exclude = ()

    def checker(field: str) -> bool:
        return field in include and field not in exclude

    return checker


def is_complex_field(field: FieldInfo) -> bool:
    return field_annotation_is_complex(field.annotation)


__all__ = [
    "async_safe",
    "fields_include_exclude",
    "is_complex_field",
    "is_optional",
    "is_seq",
    "lenient_issubclass",
    "unwrap_annotated",
    "unwrap_optional_type",
    "unwrap_seq_type",
    "unwrap_type",
]
