from enum import Enum
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Protocol,
    Union,
)

from typing_extensions import TypeAlias

from .fields import FilterField

AbstractFilterOperator: TypeAlias = Enum
FilterAliasGenerator: TypeAlias = Callable[
    [str, AbstractFilterOperator, Optional[str]],
    str,
]
FilterPlace: TypeAlias = Callable[..., Any]
FilterFieldDef: TypeAlias = Union[type[Any], FilterField[Any]]
FilterValues: TypeAlias = dict[str, dict[AbstractFilterOperator, Any]]


class FiltersResolver(Protocol):
    __model__: type[Any]
    __defs__: dict[str, tuple[str, AbstractFilterOperator]]
    __filters__: dict[str, FilterField[Any]]

    async def __call__(self, _: Any, /) -> FilterValues:  # pragma: no cover
        pass


SortingDirection: TypeAlias = Literal["asc", "desc"]
SortingNulls: TypeAlias = Optional[Literal["bigger", "smaller"]]
SortingValues: TypeAlias = list[tuple[str, SortingDirection, SortingNulls]]


class SortingResolver(Protocol):
    __tp__: Any
    __defs__: dict[str, tuple[str, SortingDirection, SortingNulls]]

    async def __call__(self, _: Any, /) -> SortingValues:  # pragma: no cover
        pass


__all__ = [
    "AbstractFilterOperator",
    "FilterAliasGenerator",
    "FilterFieldDef",
    "FilterPlace",
    "FilterValues",
    "FiltersResolver",
    "SortingDirection",
    "SortingNulls",
    "SortingResolver",
    "SortingValues",
]
