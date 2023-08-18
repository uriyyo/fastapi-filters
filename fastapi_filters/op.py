from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol

from .operators import FilterOperator

if TYPE_CHECKING:
    from .types import AbstractFilterOperator, FilterValues


@dataclass(frozen=True)
class FilterOp:
    name: str
    operator: AbstractFilterOperator
    value: Any


def simple_op(operator: AbstractFilterOperator) -> Callable[[FilterOpBuilderMixin, Any], FilterOp]:
    def func(self: FilterOpBuilderMixin, value: Any) -> FilterOp:
        self.check_op(operator)
        return FilterOp(self.name, operator, value)

    return func


class _HasNameAdnOperators(Protocol):
    name: str | None
    operators: list[AbstractFilterOperator] | None


@dataclass(frozen=True)
class FilterOpBuilderMixin:
    name: str
    operators: list[AbstractFilterOperator]

    def check_op(self, operator: AbstractFilterOperator) -> None:
        assert operator in self.operators, f"Operator {operator} is not allowed for {self.name}"

    __eq__ = simple_op(FilterOperator.eq)  # type: ignore
    __ne__ = simple_op(FilterOperator.ne)  # type: ignore
    __lt__ = simple_op(FilterOperator.lt)
    __le__ = simple_op(FilterOperator.le)
    __gt__ = simple_op(FilterOperator.gt)
    __ge__ = simple_op(FilterOperator.ge)

    eq = __eq__  # type: ignore
    ne = __ne__  # type: ignore
    lt = __lt__
    le = __le__
    gt = __gt__
    ge = __ge__

    in_ = simple_op(FilterOperator.in_)
    not_in = simple_op(FilterOperator.not_in)

    like = simple_op(FilterOperator.like)
    not_like = simple_op(FilterOperator.not_like)
    ilike = simple_op(FilterOperator.ilike)

    is_null = simple_op(FilterOperator.is_null)

    ov = simple_op(FilterOperator.ov)
    not_ov = simple_op(FilterOperator.not_ov)
    contains = simple_op(FilterOperator.contains)
    not_contains = simple_op(FilterOperator.not_contains)


def ops_to_filter_values(*ops: FilterOp) -> FilterValues:
    values: FilterValues = {}
    for op in ops:
        values.setdefault(op.name, {})

        if op.operator in values[op.name]:
            raise ValueError(f"Duplicate operator {op.operator} for {op.name}")

        values[op.name][op.operator] = op.value

    return values


__all__ = [
    "FilterOp",
    "FilterOpBuilderMixin",
    "ops_to_filter_values",
]
