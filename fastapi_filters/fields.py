from __future__ import annotations

from collections.abc import Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeVar,
    overload,
)

from pydantic_core import core_schema

from fastapi_filters.errors import InvalidDefaultOperatorError

from .op import FilterOpBuilder
from .operators import FilterOperator, get_filter_operators
from .utils import is_seq

if TYPE_CHECKING:
    from .types import AbstractFilterOperator


T_co = TypeVar("T_co", covariant=True)


class FilterField(FilterOpBuilder[T_co]):
    __fields__: ClassVar[tuple[str, ...]] = (
        "type",
        "operators",
        "default_op",
        "name",
        "alias",
        "internal",
        "op_types",
    )

    def __init__(
        self,
        type: type[T_co] | None = None,  # noqa: A002
        operators: list[AbstractFilterOperator] | None = None,
        default_op: AbstractFilterOperator | None = None,
        name: str | None = None,
        alias: str | None = None,
        internal: bool = False,
        op_types: dict[AbstractFilterOperator, Any] | None = None,
    ) -> None:
        self.type = type
        self.operators = operators
        self.default_op = default_op
        self.name = name
        self.alias = alias
        self.internal = internal
        self.op_types = op_types

        self._resolve()

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> FilterField[T_co]:
            pass

        @overload
        def __get__(
            self,
            instance: object,
            owner: Any,
        ) -> dict[AbstractFilterOperator, T_co | Sequence[T_co] | bool]:
            pass

        def __get__(self, instance: object | None, owner: Any) -> Any:
            pass

    def _resolve(self) -> None:
        if self.operators is None and self.type is not None:
            self.operators = [*get_filter_operators(self.type)]

        if self.default_op is None:
            if is_seq(self.type):
                self.default_op = FilterOperator.overlap
            else:
                self.default_op = FilterOperator.eq

        if self.default_op and self.operators is not None and self.default_op not in self.operators:
            raise InvalidDefaultOperatorError(f"default_op {self.default_op} is not in operators {self.operators}")

    def replace(self, **changes: Any) -> FilterField[Any]:
        params: dict[str, Any] = {name: getattr(self, name) for name in self.__fields__}
        return FilterField(**{**params, **changes})

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> core_schema.CoreSchema:
        # we don't care about validation, so accept anything as field core type
        return core_schema.with_default_schema(core_schema.any_schema(), default=None)

    def __repr__(self) -> str:
        args = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__fields__)
        return f"{self.__class__.__name__}({args})"

    def __hash__(self) -> int:
        return hash((self.name, self.alias, self.type))


__all__ = [
    "FilterField",
]
