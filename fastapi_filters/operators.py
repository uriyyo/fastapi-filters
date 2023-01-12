from datetime import date, datetime, timedelta
from enum import Enum
from typing import Iterator

from pydantic.utils import lenient_issubclass
from .utils import is_list


class Operators(str, Enum):
    eq = "eq"
    ne = "ne"
    gt = "gt"
    ge = "ge"
    lt = "lt"
    le = "le"
    in_ = "in"
    not_in = "not_in"
    is_null = "is_null"
    ov = "ov"
    not_ov = "not_ov"


DEFAULT_OPERATORS = [
    Operators.eq,
    Operators.ne,
    Operators.in_,
    Operators.not_in,
    Operators.is_null,
]

NUMERIC_OPERATORS = [
    Operators.gt,
    Operators.ge,
    Operators.lt,
    Operators.le,
]

LIST_OPERATORS = [
    Operators.ov,
    Operators.not_ov,
]


def get_operators(t: type) -> Iterator[Operators]:
    if is_list(t):
        yield from LIST_OPERATORS
        return

    if lenient_issubclass(t, bool):
        yield Operators.eq
        return

    yield from DEFAULT_OPERATORS

    if lenient_issubclass(t, (int, float, date, datetime, timedelta)):
        yield from NUMERIC_OPERATORS


__all__ = [
    "Operators",
    "get_operators",
]
