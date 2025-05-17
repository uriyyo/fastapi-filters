from collections.abc import Mapping
from typing import Any, TypeVar, cast

from tortoise.queryset import QuerySet

from fastapi_filters import FilterOperator, FilterSet, FilterValues
from fastapi_filters.types import AbstractFilterOperator, SortingValues

TStmt = TypeVar("TStmt", bound=QuerySet[Any])


DEFAULT_FILTERS: Mapping[AbstractFilterOperator, str] = {
    FilterOperator.eq: "",
    FilterOperator.ne: "__not",
    FilterOperator.gt: "__gt",
    FilterOperator.ge: "__ge",
    FilterOperator.lt: "__lt",
    FilterOperator.le: "__le",
    FilterOperator.like: "__like",
    FilterOperator.not_like: "__not_like",
    FilterOperator.ilike: "__ilike",
    FilterOperator.not_ilike: "__not_ilike",
    FilterOperator.in_: "__in",
    FilterOperator.not_in: "__not_in",
    FilterOperator.is_null: "__is_null",
    FilterOperator.contains: "__contains",
    FilterOperator.not_contains: "__not_contains",
}


def apply_filters(
    stmt: TStmt,
    filters: FilterValues | FilterSet,
    *,
    remapping: Mapping[str, str] | None = None,
) -> TStmt:
    remapping = remapping or {}
    if isinstance(filters, FilterSet):
        filters = filters.filter_values

    for field, field_filters in filters.items():
        field = remapping.get(field, field)
        field = field.replace(".", "__")

        for op, val in field_filters.items():
            if (cond := DEFAULT_FILTERS.get(op)) is not None:
                stmt = cast(TStmt, stmt.filter(**{f"{field}{cond}": val}))
            else:
                raise NotImplementedError(f"Operator {op} is not implemented")

    return stmt


def apply_sorting(
    stmt: TStmt,
    sorting: SortingValues,
    remapping: Mapping[str, str] | None = None,
) -> TStmt:
    remapping = remapping or {}
    ordering = []
    for field, direction, _ in sorting:
        field = remapping.get(field, field)
        field = field.replace(".", "__")
        ordering.append(f"{'-' if direction == 'desc' else ''}{field}")

    if ordering:
        stmt = stmt.order_by(*ordering)  # type: ignore[assignment]

    return stmt


def apply_filters_and_sorting(
    stmt: TStmt,
    filters: FilterValues | FilterSet,
    sorting: SortingValues,
    *,
    remapping: Mapping[str, str] | None = None,
) -> TStmt:
    stmt = apply_filters(stmt, filters, remapping=remapping)
    return apply_sorting(stmt, sorting, remapping=remapping)


__all__ = [
    "apply_filters",
    "apply_filters_and_sorting",
    "apply_sorting",
]
