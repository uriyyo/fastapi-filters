from typing import Dict, Any, Protocol, Tuple, Type
from typing_extensions import TypeAlias

from .operators import Operators


FilterValues: TypeAlias = Dict[str, Dict[Operators, Any]]


class FiltersResolver(Protocol):
    __model__: Type[Any]
    __defs__: Dict[str, Tuple[str, Operators]]

    async def __call__(self, _: Any, /) -> FilterValues:  # pragma: no cover
        pass


__all__ = [
    "FilterValues",
    "FiltersResolver",
]
