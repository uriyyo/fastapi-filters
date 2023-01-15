from dataclasses import dataclass
from typing import Type, Any, Optional, List

from .operators import FilterOperator, get_filter_operators
from .utils import is_seq


@dataclass
class FieldFilter:
    type: Type[Any]
    operators: Optional[List[FilterOperator]] = None
    default_op: Optional[FilterOperator] = None

    def __post_init__(self) -> None:
        if self.operators is None:
            self.operators = [*get_filter_operators(self.type)]

        if self.default_op is None:
            if is_seq(self.type):
                self.default_op = FilterOperator.ov
            else:
                self.default_op = FilterOperator.eq


__all__ = [
    "FieldFilter",
]
