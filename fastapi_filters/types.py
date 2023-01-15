from typing import Dict, Any, Protocol, Tuple, Type, Callable, Union
from typing_extensions import TypeAlias

from .fields import FieldFilter
from .operators import FilterOperator

FilterAliasGenerator: TypeAlias = Callable[[str, FilterOperator], str]
FilterPlace: TypeAlias = Callable[..., Any]
FilterFieldDef: TypeAlias = Union[Type[Any], FieldFilter]
FilterValues: TypeAlias = Dict[str, Dict[FilterOperator, Any]]


class FiltersResolver(Protocol):
    __model__: Type[Any]
    __defs__: Dict[str, Tuple[str, FilterOperator]]

    async def __call__(self, _: Any, /) -> FilterValues:  # pragma: no cover
        pass


__all__ = [
    "FilterAliasGenerator",
    "FilterPlace",
    "FilterFieldDef",
    "FilterValues",
    "FiltersResolver",
]
