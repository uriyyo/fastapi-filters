from datetime import date, datetime, timedelta
from enum import Enum
from typing import Iterator

from pydantic.utils import lenient_issubclass
from .utils import is_seq, is_optional, unwrap_type, unwrap_optional_type


class FilterOperator(str, Enum):
    eq = "eq"
    ne = "ne"
    gt = "gt"
    ge = "ge"
    lt = "lt"
    le = "le"
    like = "like"
    not_like = "not_like"
    ilike = "ilike"
    not_ilike = "not_ilike"
    in_ = "in"
    not_in = "not_in"
    is_null = "is_null"
    ov = "ov"
    not_ov = "not_ov"
    contains = "contains"
    not_contains = "not_contains"

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


DEFAULT_OPERATORS = [
    FilterOperator.eq,
    FilterOperator.ne,
    FilterOperator.in_,
    FilterOperator.not_in,
]

NUMERIC_OPERATORS = [
    FilterOperator.gt,
    FilterOperator.ge,
    FilterOperator.lt,
    FilterOperator.le,
]

STRING_OPERATORS = [
    FilterOperator.like,
    FilterOperator.ilike,
    FilterOperator.not_like,
    FilterOperator.not_ilike,
]

SEQ_OPERATORS = [
    FilterOperator.ov,
    FilterOperator.not_ov,
    FilterOperator.contains,
    FilterOperator.not_contains,
]


def get_filter_operators(t: type) -> Iterator[FilterOperator]:
    if is_optional(t):
        t = unwrap_optional_type(t)
        yield FilterOperator.is_null

    if is_seq(t):
        yield from SEQ_OPERATORS
        return

    tp = unwrap_type(t)

    if lenient_issubclass(tp, bool):
        yield FilterOperator.eq
        return

    yield from DEFAULT_OPERATORS

    if lenient_issubclass(tp, str):
        yield from STRING_OPERATORS

    if lenient_issubclass(tp, (int, float, date, datetime, timedelta)):
        yield from NUMERIC_OPERATORS


__all__ = [
    "SEQ_OPERATORS",
    "DEFAULT_OPERATORS",
    "NUMERIC_OPERATORS",
    "STRING_OPERATORS",
    "FilterOperator",
    "get_filter_operators",
]
