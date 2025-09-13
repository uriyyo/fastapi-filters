from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    overload,
)

from .op import FilterOpBuilder

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


T_co = TypeVar("T_co", covariant=True)


@dataclass(eq=False, order=False)
class FilterField(FilterOpBuilder[T_co]):
    type: type[T_co] | None = None
    operators: list[AbstractFilterOperator] | None = None
    default_op: AbstractFilterOperator | None = None
    name: str | None = None
    alias: str | None = None
    internal: bool = False
    op_types: dict[AbstractFilterOperator, Any] | None = None

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> FilterField[T_co]:
            pass

        @overload
        def __get__(
            self,
            instance: object,
            owner: Any,
        ) -> dict[AbstractFilterOperator, T_co | Sequence[T_co] | bool]:
            pass

        def __get__(self, instance: object | None, owner: Any) -> Any:
            pass

    def __hash__(self) -> int:
        return hash((self.name, self.alias, self.type))

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name


__all__ = [
    "FilterField",
]
