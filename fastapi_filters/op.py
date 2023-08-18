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


def _simple_op(operator: AbstractFilterOperator) -> Callable[[_HasNameAndOperatorsProtocol, Any], FilterOp]:
    def func(self: _HasNameAndOperatorsProtocol, value: Any) -> FilterOp:
        self.check_op(operator)
        return FilterOp(self.name, operator, value)  # type: ignore

    return func


class _HasNameAndOperatorsProtocol(Protocol):
    name: str | None
    operators: list[AbstractFilterOperator] | None

    def check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        pass


class FilterOpBuilderMixin:
    def check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        assert self.operators is not None, "FilterField must be assigned to a class attribute"
        assert self.name is not None, "FilterField must be assigned to a class attribute"

        assert operator in self.operators, f"Operator {operator} is not allowed for field {self.name!r}"

    __eq__ = _simple_op(FilterOperator.eq)  # type: ignore
    __ne__ = _simple_op(FilterOperator.ne)  # type: ignore
    __lt__ = _simple_op(FilterOperator.lt)
    __le__ = _simple_op(FilterOperator.le)
    __gt__ = _simple_op(FilterOperator.gt)
    __ge__ = _simple_op(FilterOperator.ge)

    eq = __eq__  # type: ignore
    ne = __ne__  # type: ignore
    lt = __lt__
    le = __le__
    gt = __gt__
    ge = __ge__

    in_ = _simple_op(FilterOperator.in_)
    not_in = _simple_op(FilterOperator.not_in)

    like = _simple_op(FilterOperator.like)
    not_like = _simple_op(FilterOperator.not_like)
    ilike = _simple_op(FilterOperator.ilike)

    is_null = _simple_op(FilterOperator.is_null)

    ov = _simple_op(FilterOperator.ov)
    not_ov = _simple_op(FilterOperator.not_ov)
    contains = _simple_op(FilterOperator.contains)
    not_contains = _simple_op(FilterOperator.not_contains)


def create_filters_from_ops(*ops: FilterOp) -> FilterValues:
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
    "create_filters_from_ops",
]
