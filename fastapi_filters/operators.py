from __future__ import annotations
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Iterator, Container, Callable, TYPE_CHECKING

from .config import ConfigVar
from .utils import is_seq, is_optional, unwrap_type, unwrap_optional_type, lenient_issubclass, unwrap_annotated

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


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

NUM_OPERATORS = [
    FilterOperator.gt,
    FilterOperator.ge,
    FilterOperator.lt,
    FilterOperator.le,
]

BOOL_OPERATORS = [
    FilterOperator.eq,
    FilterOperator.ne,
]

STR_OPERATORS = [
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


def default_filter_operators_generator(t: type) -> Iterator[AbstractFilterOperator]:
    t = unwrap_annotated(t)

    if is_optional(t):
        t = unwrap_optional_type(t)
        yield FilterOperator.is_null

    if is_seq(t):
        yield from SEQ_OPERATORS
        return

    tp = unwrap_type(t)

    if lenient_issubclass(tp, bool):
        yield from BOOL_OPERATORS
        return

    yield from DEFAULT_OPERATORS

    if lenient_issubclass(tp, str):
        yield from STR_OPERATORS

    if lenient_issubclass(tp, (int, float, date, datetime, timedelta)):
        yield from NUM_OPERATORS


disabled_filters_config: ConfigVar[Container[AbstractFilterOperator]] = ConfigVar(
    "disabled_filters",
    default=(),
)
filter_operators_generator_config: ConfigVar[Callable[[type], Iterator[AbstractFilterOperator]]] = ConfigVar(
    "filter_operators_generator",
    default=default_filter_operators_generator,
)


def get_filter_operators(t: type) -> Iterator[AbstractFilterOperator]:
    disabled = disabled_filters_config.get()
    operator_generator = filter_operators_generator_config.get()

    for op in operator_generator(t):
        if op not in disabled:
            yield op


__all__ = [
    "SEQ_OPERATORS",
    "DEFAULT_OPERATORS",
    "NUM_OPERATORS",
    "STR_OPERATORS",
    "FilterOperator",
    "default_filter_operators_generator",
    "get_filter_operators",
    "disabled_filters_config",
    "filter_operators_generator_config",
]
