from enum import Enum
from typing import Dict, Any, Protocol, Tuple, Type, Callable, Union
from typing_extensions import TypeAlias

from .fields import FieldFilter

AbstractFilterOperator: TypeAlias = Enum
FilterAliasGenerator: TypeAlias = Callable[[str, AbstractFilterOperator], str]
FilterPlace: TypeAlias = Callable[..., Any]
FilterFieldDef: TypeAlias = Union[Type[Any], FieldFilter]
FilterValues: TypeAlias = Dict[str, Dict[AbstractFilterOperator, Any]]


class FiltersResolver(Protocol):
    __model__: Type[Any]
    __defs__: Dict[str, Tuple[str, AbstractFilterOperator]]

    async def __call__(self, _: Any, /) -> FilterValues:  # pragma: no cover
        pass


__all__ = [
    "AbstractFilterOperator",
    "FilterAliasGenerator",
    "FilterPlace",
    "FilterFieldDef",
    "FilterValues",
    "FiltersResolver",
]
