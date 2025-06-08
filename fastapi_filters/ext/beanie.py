from collections.abc import Callable, Mapping
from typing import Any, TypeVar, cast

from beanie import SortDirection
from beanie.odm.operators.find import BaseFindOperator
from beanie.odm.operators.find.comparison import GT, GTE, LT, LTE, NE, Eq, In, NotIn
from beanie.odm.operators.find.evaluation import RegEx
from beanie.odm.operators.find.logical import Not
from beanie.odm.queries.find import FindMany

from fastapi_filters import FilterOperator, FilterSet, FilterValues
from fastapi_filters.types import AbstractFilterOperator, SortingValues

DEFAULT_FILTERS: Mapping[AbstractFilterOperator, Callable[..., BaseFindOperator]] = {
    FilterOperator.eq: Eq,
    FilterOperator.ne: NE,
    FilterOperator.gt: GT,
    FilterOperator.ge: GTE,
    FilterOperator.lt: LT,
    FilterOperator.le: LTE,
    FilterOperator.like: RegEx,
    FilterOperator.not_like: lambda field, val: Not(RegEx(field, val)),
    FilterOperator.ilike: lambda field, val: RegEx(field, val, options="i"),
    FilterOperator.not_ilike: lambda field, val: Not(RegEx(field, val, options="i")),
    FilterOperator.in_: In,
    FilterOperator.not_in: NotIn,
    FilterOperator.is_null: lambda field, val: Eq(field, None) if val else NE(field, None),
    FilterOperator.contains: In,
    FilterOperator.not_contains: NotIn,
    FilterOperator.overlap: In,
    FilterOperator.not_overlap: NotIn,
}


TStmt = TypeVar("TStmt", bound=FindMany[Any])


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

        for op, val in field_filters.items():
            stmt.find()

            if (cond := DEFAULT_FILTERS.get(op)) is not None:
                stmt = cast(TStmt, stmt.find(cond(field, val)))
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

        if direction == "asc":
            ordering.append((field, SortDirection.ASCENDING))
        else:
            ordering.append((field, SortDirection.DESCENDING))

    if ordering:
        stmt = cast(TStmt, stmt.sort(*ordering))

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
