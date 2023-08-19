from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol, Generic, TypeVar, Sequence, Optional, overload

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

    @abstractmethod
    def _check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        pass


T = TypeVar("T", covariant=True)
TArg = TypeVar("TArg")


class FilterOpBuilder(Generic[T]):
    def _check_op(self: _HasNameAndOperatorsProtocol, operator: AbstractFilterOperator) -> None:
        assert self.operators is not None, "FilterField has no operators"
        assert self.name is not None, "FilterField has no name"

        assert operator in self.operators, f"Operator {operator} is not allowed for field {self.name!r}"

    def __call__(self: _HasNameAndOperatorsProtocol, op: AbstractFilterOperator, value: TArg) -> FilterOp[TArg]:
        self._check_op(op)
        return FilterOp(self.name, op, value)  # type: ignore

    if TYPE_CHECKING:

        @overload  # we need special overload case for str because it is a Sequence of strings
        def __scalar_method_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[str], value: str, /
        ) -> FilterOp[str]:
            pass

        @overload
        def __scalar_method_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[Sequence[TArg]], value: Any, /
        ) -> None:
            pass

        @overload
        def __scalar_method_scalar_arg__(self: FilterOpBuilder[TArg], value: TArg, /) -> FilterOp[TArg]:
            pass

        def __scalar_method_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __scalar_method_non_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[str], value: str, /
        ) -> FilterOp[str]:
            pass

        @overload
        def __scalar_method_non_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[Sequence[TArg]], value: Any, /
        ) -> None:
            pass

        @overload
        def __scalar_method_non_scalar_arg__(
            self: FilterOpBuilder[TArg],
            value: Sequence[TArg],
            /,
        ) -> FilterOp[TArg]:
            pass

        def __scalar_method_non_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[str], value: str, /
        ) -> None:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[Sequence[TArg]], value: Sequence[TArg], /
        ) -> FilterOp[Sequence[TArg]]:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(self: FilterOpBuilder[TArg], value: TArg, /) -> None:
            pass

        def __non_scalar_method_non_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __non_scalar_method_scalar_arg__(self: FilterOpBuilder[str], value: str, /) -> None:  # type: ignore[misc]
            pass

        @overload
        def __non_scalar_method_scalar_arg__(  # type: ignore[misc]
            self: FilterOpBuilder[Sequence[TArg]], value: TArg, /
        ) -> FilterOp[TArg]:
            pass

        @overload
        def __non_scalar_method_scalar_arg__(self: FilterOpBuilder[TArg], value: TArg, /) -> None:
            pass

        def __non_scalar_method_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __eq__(self: FilterOpBuilder[str], value: str, /) -> FilterOp[str]:  # type: ignore[misc]
            pass

        @overload
        def __eq__(self: FilterOpBuilder[Sequence[TArg]], value: Any, /) -> None:  # type: ignore[misc]
            pass

        @overload
        def __eq__(self: FilterOpBuilder[TArg], value: TArg, /) -> FilterOp[TArg]:  # type: ignore[misc]
            pass

        @overload
        def __eq__(self: object, value: object, /) -> bool:
            pass

        def __eq__(self, value: Any) -> Any:
            pass

        __ne__ = __eq__
        __lt__ = __eq__
        __le__ = __eq__
        __gt__ = __eq__
        __ge__ = __eq__

        eq = __scalar_method_scalar_arg__
        ne = __scalar_method_scalar_arg__
        lt = __scalar_method_scalar_arg__
        le = __scalar_method_scalar_arg__
        gt = __scalar_method_scalar_arg__
        ge = __scalar_method_scalar_arg__

        in_ = __scalar_method_non_scalar_arg__
        not_in = __scalar_method_non_scalar_arg__

        __rshift__ = __scalar_method_non_scalar_arg__  # >> as in operator

        def like(self: FilterOpBuilder[str], value: str, /) -> FilterOp[str]:
            pass

        not_like = like
        ilike = like
        not_ilike = like

        ov = __non_scalar_method_non_scalar_arg__
        not_ov = __non_scalar_method_non_scalar_arg__

        contains = __non_scalar_method_scalar_arg__
        not_contains = __non_scalar_method_scalar_arg__

        def is_null(self: FilterOpBuilder[Optional[TArg]], value: bool, /) -> FilterOp[bool]:
            pass

    else:
        __eq__ = _simple_op(FilterOperator.eq)
        __ne__ = _simple_op(FilterOperator.ne)
        __lt__ = _simple_op(FilterOperator.lt)
        __le__ = _simple_op(FilterOperator.le)
        __gt__ = _simple_op(FilterOperator.gt)
        __ge__ = _simple_op(FilterOperator.ge)

        eq = __eq__
        ne = __ne__
        lt = __lt__
        le = __le__
        gt = __gt__
        ge = __ge__

        in_ = _simple_op(FilterOperator.in_)
        not_in = _simple_op(FilterOperator.not_in)

        __rshift__ = in_  # >> as in operator

        like = _simple_op(FilterOperator.like)
        not_like = _simple_op(FilterOperator.not_like)
        ilike = _simple_op(FilterOperator.ilike)
        not_ilike = _simple_op(FilterOperator.not_ilike)

        ov = _simple_op(FilterOperator.ov)
        not_ov = _simple_op(FilterOperator.not_ov)
        contains = _simple_op(FilterOperator.contains)
        not_contains = _simple_op(FilterOperator.not_contains)

        def is_null(self: _HasNameAndOperatorsProtocol, val: bool = True, /) -> FilterOp[bool]:
            self._check_op(FilterOperator.is_null)
            return FilterOp(self.name, FilterOperator.is_null, val)


__all__ = [
    "FilterOp",
    "FilterOpBuilder",
]
