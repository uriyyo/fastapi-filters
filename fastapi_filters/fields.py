from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    overload,
)

from fastapi_filters.errors import InvalidDefaultOperatorError

from .op import FilterOpBuilder
from .operators import FilterOperator, get_filter_operators
from .utils import is_optional, is_seq, unwrap_annotated, unwrap_optional_type

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


T_co = TypeVar("T_co", covariant=True)


def _is_sequence_type(tp: Any) -> bool:
    tp = unwrap_annotated(tp)

    if is_optional(tp):
        tp = unwrap_optional_type(tp)

    return is_seq(tp)


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

    def __post_init__(self) -> None:
        if self.operators is None and self.type is not None:
            self.operators = [*get_filter_operators(self.type)]

        if self.default_op is None:
            if _is_sequence_type(self.type):
                self.default_op = FilterOperator.overlap
            else:
                self.default_op = FilterOperator.eq

        if self.default_op and self.operators is not None and self.default_op not in self.operators:
            raise InvalidDefaultOperatorError(f"default_op {self.default_op} is not in operators {self.operators}")


__all__ = [
    "FilterField",
]
