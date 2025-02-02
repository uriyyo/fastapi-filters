from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    TypeVar,
    Union,
    overload,
)

from .op import FilterOpBuilder
from .operators import FilterOperator, get_filter_operators
from .utils import is_seq

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


T_co = TypeVar("T_co", covariant=True)


@dataclass(eq=False, order=False)
class FilterField(FilterOpBuilder[T_co]):
    type: Optional[type[T_co]] = None
    operators: Optional[list[AbstractFilterOperator]] = None
    default_op: Optional[AbstractFilterOperator] = None
    name: Optional[str] = None
    alias: Optional[str] = None
    internal: bool = False
    op_types: Optional[dict[AbstractFilterOperator, Any]] = None

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> FilterField[T_co]:
            pass

        @overload
        def __get__(
            self,
            instance: object,
            owner: Any,
        ) -> dict[AbstractFilterOperator, Union[T_co, Sequence[T_co], bool]]:
            pass

        def __get__(self, instance: Optional[object], owner: Any) -> Any:
            pass

    def __hash__(self) -> int:
        return hash((self.name, self.alias, self.type))

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    def __post_init__(self) -> None:
        if self.operators is None and self.type is not None:
            self.operators = [*get_filter_operators(self.type)]

        if self.default_op is None:
            if is_seq(self.type):
                self.default_op = FilterOperator.overlap
            else:
                self.default_op = FilterOperator.eq


__all__ = [
    "FilterField",
]
