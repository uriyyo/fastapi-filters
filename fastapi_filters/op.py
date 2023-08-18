from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol, Generic, TypeVar, Sequence
from typing_extensions import Self

from .operators import FilterOperator

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


TVal = TypeVar("TVal", covariant=True)


@dataclass(frozen=True)
class FilterOp(Generic[TVal]):
    name: str
    operator: AbstractFilterOperator
    value: TVal


def _simple_op(operator: AbstractFilterOperator) -> Callable[[_HasNameAndOperatorsProtocol, Any], FilterOp[Any]]:
    def func(self: _HasNameAndOperatorsProtocol, value: Any) -> FilterOp[Any]:
        self._check_op(operator)
        return FilterOp(self.name, operator, value)  # type: ignore

    func.__name__ = operator.name
    return func


class _HasNameAndOperatorsProtocol(Protocol):
    name: str | None
    operators: list[AbstractFilterOperator] | None

    def _check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        pass


T = TypeVar("T", covariant=True)

TArg = TypeVar("TArg")
TOther = TypeVar("TOther")

_OpFunc = Callable[[TArg, TOther], FilterOp[TOther]]


class FilterOpBuilderMixin(Generic[T]):
    def _check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        assert self.operators is not None, "FilterField must be assigned to a class attribute"
        assert self.name is not None, "FilterField must be assigned to a class attribute"

        assert operator in self.operators, f"Operator {operator} is not allowed for field {self.name!r}"

    def __call__(self: _HasNameAndOperatorsProtocol, op: AbstractFilterOperator, value: TArg) -> FilterOp[TArg]:
        self._check_op(op)
        return FilterOp(self.name, op, value)  # type: ignore

    if TYPE_CHECKING:
        __eq__: _OpFunc[Self, T]  # type: ignore[assignment]
        __ne__: _OpFunc[Self, T]  # type: ignore[assignment]
        __lt__: _OpFunc[Self, T]
        __le__: _OpFunc[Self, T]
        __gt__: _OpFunc[Self, T]
        __ge__: _OpFunc[Self, T]

        in_: _OpFunc[Self, Sequence[T]]
        not_in: _OpFunc[Self, Sequence[T]]

        like: _OpFunc[Self, T]
        not_like: _OpFunc[Self, T]
        ilike: _OpFunc[Self, T]

        is_null: _OpFunc[Self, bool]

        ov: _OpFunc[Self, Sequence[T]]
        not_ov: _OpFunc[Self, Sequence[T]]
        contains: _OpFunc[Self, T]
        not_contains: _OpFunc[Self, T]
    else:
        __eq__ = _simple_op(FilterOperator.eq)
        __ne__ = _simple_op(FilterOperator.ne)
        __lt__ = _simple_op(FilterOperator.lt)
        __le__ = _simple_op(FilterOperator.le)
        __gt__ = _simple_op(FilterOperator.gt)
        __ge__ = _simple_op(FilterOperator.ge)

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

    eq = __eq__
    ne = __ne__
    lt = __lt__
    le = __le__
    gt = __gt__
    ge = __ge__

    __rshift__ = in_  # >> as in operator


__all__ = [
    "FilterOp",
    "FilterOpBuilderMixin",
]
