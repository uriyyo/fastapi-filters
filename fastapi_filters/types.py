from enum import Enum
from typing import Dict, Any, Protocol, Tuple, Type, Callable, Union, Literal, List, Optional
from typing_extensions import TypeAlias

from .fields import FilterField

AbstractFilterOperator: TypeAlias = Enum
FilterAliasGenerator: TypeAlias = Callable[[str, AbstractFilterOperator], str]
FilterPlace: TypeAlias = Callable[..., Any]
FilterFieldDef: TypeAlias = Union[Type[Any], FilterField]
FilterValues: TypeAlias = Dict[str, Dict[AbstractFilterOperator, Any]]


class FiltersResolver(Protocol):
    __model__: Type[Any]
    __defs__: Dict[str, Tuple[str, AbstractFilterOperator]]
    __filters__: Dict[str, FilterField[Any]]

    async def __call__(self, _: Any, /) -> FilterValues:  # pragma: no cover
        pass


SortingDirection: TypeAlias = Literal["asc", "desc"]
SortingNulls: TypeAlias = Optional[Literal["bigger", "smaller"]]
SortingValues: TypeAlias = List[Tuple[str, SortingDirection, SortingNulls]]


class SortingResolver(Protocol):
    __tp__: Any
    __defs__: Dict[str, Tuple[str, SortingDirection, SortingNulls]]

    async def __call__(self, _: Any, /) -> SortingValues:  # pragma: no cover
        pass


__all__ = [
    "AbstractFilterOperator",
    "FilterAliasGenerator",
    "FilterPlace",
    "FilterFieldDef",
    "FilterValues",
    "FiltersResolver",
    "SortingDirection",
    "SortingNulls",
    "SortingValues",
    "SortingResolver",
]
