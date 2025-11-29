from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
    overload,
)

from .operators import FilterOperator

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


TVal_co = TypeVar("TVal_co", covariant=True)


@dataclass(frozen=True)
class FilterOp(Generic[TVal_co]):
    name: str
    operator: AbstractFilterOperator
    value: TVal_co


def _simple_op(
    operator: AbstractFilterOperator,
) -> Callable[[_HasNameAndOperatorsProtocol, Any], FilterOp[Any]]:
    def func(self: _HasNameAndOperatorsProtocol, value: Any) -> FilterOp[Any]:
        self._check_op(operator)
        return FilterOp(self.name, operator, value)  # type: ignore[arg-type]

    func.__name__ = operator.name
    return func


class _HasNameAndOperatorsProtocol(Protocol):
    name: str | None
    operators: list[AbstractFilterOperator] | None

    @abstractmethod
    def _check_op(
        self: _HasNameAndOperatorsProtocol,
        operator: AbstractFilterOperator,
    ) -> None:
        pass


T_co = TypeVar("T_co", covariant=True)
TArg_co = TypeVar("TArg_co", covariant=True)


class FilterOpBuilder(Generic[T_co]):  # noqa: PLW1641
    def _check_op(
        self: _HasNameAndOperatorsProtocol,
        operator: AbstractFilterOperator,
    ) -> None:
        assert self.operators is not None, "FilterField has no operators"
        assert self.name is not None, "FilterField has no name"

        assert operator in self.operators, f"Operator {operator} is not allowed for field {self.name!r}"

    def __call__(
        self: _HasNameAndOperatorsProtocol,
        op: AbstractFilterOperator,
        value: T_co,  # type: ignore[misc]
    ) -> FilterOp[T_co]:
        self._check_op(op)
        return FilterOp(self.name, op, value)  # type: ignore[arg-type]

    if TYPE_CHECKING:

        @overload
        def __scalar_method_scalar_arg__(
            self: FilterOpBuilder[Enum],
            value: Enum,
            /,
        ) -> FilterOp[Enum]:
            pass

        @overload  # we need special overload case for str because it is a Sequence of strings
        def __scalar_method_scalar_arg__(
            self: FilterOpBuilder[str],
            value: str,
            /,
        ) -> FilterOp[str]:
            pass

        @overload
        def __scalar_method_scalar_arg__(  # type: ignore[overload-overlap]
            self: FilterOpBuilder[Sequence[TArg_co]],
            value: Any,
            /,
        ) -> None:
            pass

        @overload
        def __scalar_method_scalar_arg__(
            self: FilterOpBuilder[TArg_co],
            value: TArg_co,  # type: ignore[misc]
            /,
        ) -> FilterOp[TArg_co]:
            pass

        def __scalar_method_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(
            self: FilterOpBuilder[str],
            value: Any,
            /,
        ) -> None:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(
            self: FilterOpBuilder[Sequence[TArg_co]],
            value: Sequence[TArg_co],
            /,
        ) -> FilterOp[Sequence[TArg_co]]:
            pass

        @overload
        def __non_scalar_method_non_scalar_arg__(
            self: FilterOpBuilder[TArg_co],
            value: Any,
            /,
        ) -> None:
            pass

        def __non_scalar_method_non_scalar_arg__(self, value: Any, /) -> Any:
            pass

        @overload
        def __eq__(self: FilterOpBuilder[Enum], value: Enum, /) -> FilterOp[Enum]:  # type: ignore[overload-overlap]
            pass

        @overload
        def __eq__(self: FilterOpBuilder[str], value: str, /) -> FilterOp[str]:  # type: ignore[overload-overlap]
            pass

        @overload
        def __eq__(self: FilterOpBuilder[Sequence[TArg_co]], value: Any, /) -> None:  # type: ignore[overload-overlap]
            pass

        @overload
        def __eq__(self: FilterOpBuilder[TArg_co], value: TArg_co, /) -> FilterOp[TArg_co]:  # type: ignore[misc]
            pass

        @overload
        def __eq__(self: object, value: object, /) -> bool:
            pass

        def __eq__(self, value: Any, /) -> Any:
            pass

        __ne__ = __eq__

        @overload
        def __lt__(self: FilterOpBuilder[bool], other: Any, /) -> None:  # type: ignore[overload-overlap]
            pass

        @overload
        def __lt__(self: FilterOpBuilder[Enum], other: Any, /) -> None:  # type: ignore[overload-overlap]
            pass

        @overload
        def __lt__(  # type: ignore[overload-overlap]
            self: FilterOpBuilder[Sequence[TArg_co]],
            other: Any,
            /,
        ) -> None:
            pass

        @overload
        def __lt__(self: FilterOpBuilder[TArg_co], other: TArg_co, /) -> FilterOp[TArg_co]:  # type: ignore[misc]
            pass

        def __lt__(self, other: Any) -> Any:
            pass

        __le__ = __lt__
        __gt__ = __lt__
        __ge__ = __lt__

        eq = __eq__
        ne = __eq__

        lt = __lt__
        le = __lt__
        gt = __lt__
        ge = __lt__

        @overload
        def __rshift__(
            self: FilterOpBuilder[Enum],
            other: Any,
            /,
        ) -> FilterOp[Sequence[Enum]]:
            pass

        @overload
        def __rshift__(self: FilterOpBuilder[bool], other: Any, /) -> None:
            pass

        @overload
        def __rshift__(self: FilterOpBuilder[Sequence[TArg_co]], other: Any, /) -> None:
            pass

        @overload
        def __rshift__(
            self: FilterOpBuilder[TArg_co],
            other: Sequence[TArg_co],
            /,
        ) -> FilterOp[Sequence[TArg_co]]:
            pass

        # >> as in operator
        def __rshift__(self, other: Any) -> Any:
            pass

        in_ = __rshift__
        not_in = __rshift__

        @overload
        def like(self: FilterOpBuilder[Enum], value: str, /) -> Any:
            pass

        @overload
        def like(self: FilterOpBuilder[str], value: str, /) -> FilterOp[str]:
            pass

        @overload
        def like(self: FilterOpBuilder[Any], value: Any, /) -> None:
            pass

        def like(self, value: Any, /) -> Any:
            pass

        not_like = like
        ilike = like
        not_ilike = like

        overlaps = __non_scalar_method_non_scalar_arg__
        not_overlaps = __non_scalar_method_non_scalar_arg__

        contains = __non_scalar_method_non_scalar_arg__
        not_contains = __non_scalar_method_non_scalar_arg__

        def is_null(self, value: bool = ..., /) -> FilterOp[bool]:
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

        overlaps = _simple_op(FilterOperator.overlap)
        not_overlaps = _simple_op(FilterOperator.not_overlap)
        contains = _simple_op(FilterOperator.contains)
        not_contains = _simple_op(FilterOperator.not_contains)

        def is_null(
            self: _HasNameAndOperatorsProtocol,
            val: bool = True,
            /,
        ) -> FilterOp[bool]:
            self._check_op(FilterOperator.is_null)
            return FilterOp(self.name, FilterOperator.is_null, val)


__all__ = [
    "FilterOp",
    "FilterOpBuilder",
]
