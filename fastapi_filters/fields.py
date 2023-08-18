from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Optional, List, TYPE_CHECKING, Generic, Any, TypeVar, overload, Union, Mapping

from .operators import FilterOperator, get_filter_operators
from .utils import is_seq

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


T = TypeVar("T", covariant=True)


@dataclass
class FieldFilter(Generic[T]):
    type: Optional[Type[T]] = None
    operators: Optional[List[AbstractFilterOperator]] = None
    default_op: Optional[AbstractFilterOperator] = None

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> FieldFilter[T]:
            pass

        @overload
        def __get__(
            self,
            instance: object,
            owner: Any,
        ) -> Optional[Mapping[AbstractFilterOperator, Union[T, List[T], bool]]]:
            pass

        def __get__(self, instance: Optional[object], owner: Any) -> Any:
            pass

    def __post_init__(self) -> None:
        if self.operators is None and self.type is not None:
            self.operators = [*get_filter_operators(self.type)]

        if self.default_op is None:
            if is_seq(self.type):
                self.default_op = FilterOperator.ov
            else:
                self.default_op = FilterOperator.eq


__all__ = [
    "FieldFilter",
]
