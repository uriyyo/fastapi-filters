from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Any, Optional, List, TYPE_CHECKING

from .operators import FilterOperator, get_filter_operators
from .utils import is_seq

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


@dataclass
class FieldFilter:
    type: Optional[Type[Any]] = None
    operators: Optional[List[AbstractFilterOperator]] = None
    default_op: Optional[AbstractFilterOperator] = None

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
