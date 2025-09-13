from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from .operators import FilterOperator, default_filter_operators_generator
from .schemas import CSVList
from .types import AbstractFilterOperator
from .utils import is_seq, unwrap_seq_type

if TYPE_CHECKING:
    from .fields import FilterField


class FilterFieldFilterDefaultOperatorsHook:
    @classmethod
    def get_default_filter_operators(
        cls,
        tp: type[Any],
    ) -> Iterable[AbstractFilterOperator]:
        yield from default_filter_operators_generator(tp)

    @classmethod
    def get_default_filter_operator(
        cls,
        tp: type[Any],
    ) -> AbstractFilterOperator:
        if is_seq(tp):
            return FilterOperator.overlap
        return FilterOperator.eq


class FilterFieldAliasHook:
    @classmethod
    def generate_filter_field_alias(
        cls,
        field: FilterField[Any],
        op: AbstractFilterOperator,
        alias: str | None = None,
    ) -> str:
        name = alias or field.alias or field.name
        return f"{name}[{op.name.rstrip('_')}]"


class FilterFieldTypeHook:
    @classmethod
    def adapt_filter_field_type(
        cls,
        field: FilterField[Any],
        tp: type[Any],
        op: AbstractFilterOperator,
    ) -> Any:
        if field.op_types and op in field.op_types:
            return field.op_types[op]

        if is_seq(tp):
            return CSVList[unwrap_seq_type(tp)]  # type: ignore[misc]

        if op in {
            FilterOperator.like,
            FilterOperator.ilike,
            FilterOperator.not_like,
            FilterOperator.not_ilike,
        }:
            return str

        if op == FilterOperator.is_null:
            return bool

        if op in {FilterOperator.in_, FilterOperator.not_in}:
            return CSVList[tp]  # type: ignore[valid-type]

        return tp


__all__ = [
    "FilterFieldAliasHook",
    "FilterFieldFilterDefaultOperatorsHook",
    "FilterFieldTypeHook",
]
