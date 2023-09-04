import operator
from contextlib import suppress
from typing import TypeVar, Mapping, Any, Callable, cast, Optional, Container, List, Iterator, Tuple, Union

from sqlalchemy.orm import ColumnProperty
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect, ARRAY, asc, desc, nulls_last, nulls_first, ColumnExpressionArgument
from typing_extensions import TypeAlias

from fastapi_filters import create_filters
from fastapi_filters.filter_set import FilterSet
from fastapi_filters.config import ConfigVar
from fastapi_filters.operators import FilterOperator
from fastapi_filters.sorters import create_sorting
from fastapi_filters.types import (
    FilterValues,
    FilterAliasGenerator,
    FilterFieldDef,
    FiltersResolver,
    FilterPlace,
    AbstractFilterOperator,
    SortingValues,
    SortingDirection,
    SortingResolver,
    SortingNulls,
)
from fastapi_filters.utils import fields_include_exclude

TSelectable = TypeVar("TSelectable", bound=Select[Any])


DEFAULT_FILTERS: Mapping[AbstractFilterOperator, Callable[[Any, Any], Any]] = {
    FilterOperator.eq: operator.eq,
    FilterOperator.ne: operator.ne,
    FilterOperator.gt: operator.gt,
    FilterOperator.ge: operator.ge,
    FilterOperator.lt: operator.lt,
    FilterOperator.le: operator.le,
    FilterOperator.like: lambda a, b: a.like(b),
    FilterOperator.not_like: lambda a, b: ~a.like(b),
    FilterOperator.ilike: lambda a, b: a.ilike(b),
    FilterOperator.not_ilike: lambda a, b: ~a.ilike(b),
    FilterOperator.in_: lambda a, b: a.in_(b),
    FilterOperator.not_in: lambda a, b: a.not_in(b),
    FilterOperator.is_null: lambda a, b: a.is_(None) if b else a.isnot(None),
    FilterOperator.overlap: lambda a, b: a.overlap(b),
    FilterOperator.not_overlap: lambda a, b: ~a.overlap(b),
    FilterOperator.contains: lambda a, b: a.contains(b),
    FilterOperator.not_contains: lambda a, b: ~a.contains(b),
}
SORT_FUNCS: Mapping[
    SortingDirection,
    Callable[[ColumnExpressionArgument[Any]], ColumnExpressionArgument[Any]],
] = {
    "asc": asc,
    "desc": desc,
}
SORT_NULLS_FUNCS: Mapping[
    Tuple[SortingDirection, SortingNulls],
    Callable[[ColumnExpressionArgument[Any]], ColumnExpressionArgument[Any]],
] = {
    ("asc", "bigger"): nulls_last,
    ("asc", "smaller"): nulls_first,
    ("desc", "bigger"): nulls_first,
    ("desc", "smaller"): nulls_last,
}

EntityNamespace: TypeAlias = Mapping[str, Any]


def _get_entity_namespace(stmt: TSelectable) -> EntityNamespace:
    ns = {}

    for entity in reversed(stmt.get_final_froms()):
        for name, clause in reversed(entity.c.items()):
            ns[name] = clause
            ns[clause.name] = clause

            with suppress(AttributeError):
                table_name = clause.table.name
                ns[f"{table_name}.{clause.name}"] = clause

                if table_name.endswith("s"):
                    ns[f"{table_name[:-1]}.{clause.name}"] = clause

    return ns


def _default_apply_filter(*_: Any) -> Any:
    raise NotImplementedError


ApplyFilterFunc: TypeAlias = Callable[[TSelectable, EntityNamespace, str, AbstractFilterOperator, Any], TSelectable]

custom_apply_filter: ConfigVar[ApplyFilterFunc[Any]] = ConfigVar(
    "apply_filter",
    default=_default_apply_filter,
)


def _apply_filter(
    stmt: TSelectable,
    ns: EntityNamespace,
    field: str,
    op: AbstractFilterOperator,
    val: Any,
    apply_filter: Optional[ApplyFilterFunc[TSelectable]] = None,
) -> TSelectable:
    custom_apply_filter_impl = custom_apply_filter.get()

    try:
        cond = None
        if apply_filter:
            try:
                cond = apply_filter(stmt, ns, field, op, val)
            except NotImplementedError:
                pass

        if cond is None:
            cond = custom_apply_filter_impl(stmt, ns, field, op, val)
    except NotImplementedError:
        try:
            cond = DEFAULT_FILTERS[op](ns[field], val)
        except KeyError:
            raise NotImplementedError(f"Operator {op} is not implemented") from None

    return stmt.where(cond)  # type: ignore[arg-type]


def apply_filters(
    stmt: TSelectable,
    filters: Union[FilterValues, FilterSet],
    *,
    remapping: Optional[Mapping[str, str]] = None,
    additional: Optional[EntityNamespace] = None,
    apply_filter: Optional[ApplyFilterFunc[TSelectable]] = None,
) -> TSelectable:
    if isinstance(filters, FilterSet):
        filters = filters.filter_values

    remapping = remapping or {}
    ns = {**_get_entity_namespace(stmt), **(additional or {})}

    for field, field_filters in filters.items():
        field = remapping.get(field, field)

        for op, val in field_filters.items():
            stmt = _apply_filter(stmt, ns, field, op, val, apply_filter)

    return stmt


def apply_sorting(
    stmt: TSelectable,
    sorting: SortingValues,
    *,
    remapping: Optional[Mapping[str, str]] = None,
    additional: Optional[EntityNamespace] = None,
) -> TSelectable:
    remapping = remapping or {}
    ns = {**_get_entity_namespace(stmt), **(additional or {})}

    for field, direction, nulls in sorting:
        field = remapping.get(field, field)

        if sort_func := SORT_FUNCS.get(direction):
            sort_expr = sort_func(ns[field])

            if nulls is not None:
                sort_expr = SORT_NULLS_FUNCS[(direction, nulls)](sort_expr)

            stmt = stmt.order_by(sort_expr)
        else:
            raise ValueError(f"Unknown sorting direction {direction}")

    return stmt


def apply_filters_and_sorting(
    stmt: TSelectable,
    filters: Union[FilterValues, FilterSet],
    sorting: SortingValues,
    *,
    remapping: Optional[Mapping[str, str]] = None,
    additional: Optional[EntityNamespace] = None,
    apply_filter: Optional[ApplyFilterFunc[TSelectable]] = None,
) -> TSelectable:
    stmt = apply_filters(stmt, filters, remapping=remapping, additional=additional, apply_filter=apply_filter)
    stmt = apply_sorting(stmt, sorting, remapping=remapping, additional=additional)

    return stmt


def adapt_sqlalchemy_column_type(column: ColumnProperty[Any]) -> FilterFieldDef:
    expr: Any = column.expression

    type_: Any
    if isinstance(expr.type, ARRAY):
        type_ = List[expr.type.item_type.python_type]
    else:
        type_ = expr.type.python_type

    if expr.nullable:
        type_ = Optional[type_]

    return cast(FilterFieldDef, type_)


def _iter_over_orm_columns(
    obj: Any,
    *,
    include_fk: bool = False,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
    remapping: Optional[Mapping[str, str]] = None,
) -> Iterator[Tuple[str, ColumnProperty[Any]]]:
    inspected = inspect(obj, raiseerr=True)

    remapping = remapping or {}
    checker = fields_include_exclude(inspected.mapper.attrs.keys(), include, exclude)

    for name, column in inspected.mapper.attrs.items():
        name = remapping.get(name, name)

        if not checker(name):
            continue

        if not isinstance(column, ColumnProperty):
            continue

        if not include_fk and getattr(column.expression, "foreign_keys", None):
            continue

        yield name, column


def create_filters_from_orm(
    obj: Any,
    *,
    in_: Optional[FilterPlace] = None,
    alias_generator: Optional[FilterAliasGenerator] = None,
    include_fk: bool = False,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
    remapping: Optional[Mapping[str, str]] = None,
    **overrides: FilterFieldDef,
) -> FiltersResolver:
    fields = {
        name: adapt_sqlalchemy_column_type(column)
        for name, column in _iter_over_orm_columns(
            obj,
            include_fk=include_fk,
            include=include,
            exclude=exclude,
            remapping=remapping,
        )
    }

    return create_filters(
        in_=in_,
        alias_generator=alias_generator,
        **{**fields, **overrides},
    )


def create_sorting_from_orm(
    obj: Any,
    *,
    default: Optional[str] = None,
    in_: Optional[FilterPlace] = None,
    include_fk: bool = False,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
    remapping: Optional[Mapping[str, str]] = None,
) -> SortingResolver:
    fields = [
        name
        for name, _ in _iter_over_orm_columns(
            obj,
            include_fk=include_fk,
            include=include,
            exclude=exclude,
            remapping=remapping,
        )
    ]

    return create_sorting(
        *fields,
        in_=in_,
        default=default,
    )


__all__ = [
    "custom_apply_filter",
    "apply_filters",
    "apply_sorting",
    "apply_filters_and_sorting",
    "adapt_sqlalchemy_column_type",
    "create_filters_from_orm",
    "create_sorting_from_orm",
]
