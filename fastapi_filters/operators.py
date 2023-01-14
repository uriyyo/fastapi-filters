from datetime import date, datetime, timedelta
from enum import Enum
from typing import Iterator

from pydantic.utils import lenient_issubclass
from .utils import is_seq, is_optional, unwrap_type


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
]

NUMERIC_OPERATORS = [
    Operators.gt,
    Operators.ge,
    Operators.lt,
    Operators.le,
]

SEQ_OPERATORS = [
    Operators.ov,
    Operators.not_ov,
]


def get_operators(t: type) -> Iterator[Operators]:
    if is_optional(t):
        yield Operators.is_null

    if is_seq(t):
        yield from SEQ_OPERATORS
        return

    tp = unwrap_type(t)

    if lenient_issubclass(tp, bool):
        yield Operators.eq
        return

    yield from DEFAULT_OPERATORS

    if lenient_issubclass(tp, (int, float, date, datetime, timedelta)):
        yield from NUMERIC_OPERATORS


__all__ = [
    "SEQ_OPERATORS",
    "DEFAULT_OPERATORS",
    "NUMERIC_OPERATORS",
    "Operators",
    "get_operators",
]
