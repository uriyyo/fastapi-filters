import operator
from contextlib import suppress
from typing import TypeVar, Mapping, Any, Callable, cast, Optional, Container, List

from sqlalchemy.orm import ColumnProperty
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect, ARRAY
from typing_extensions import TypeAlias

from fastapi_filters import create_filters
from fastapi_filters.operators import FilterOperator
from fastapi_filters.types import FilterValues, FilterAliasGenerator, FilterFieldDef, FiltersResolver, FilterPlace

TSelectable = TypeVar("TSelectable", bound=Select)


DEFAULT_FILTERS: Mapping[FilterOperator, Callable[[Any, Any], Any]] = {
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
    FilterOperator.ov: lambda a, b: a.overlap(b),
    FilterOperator.not_ov: lambda a, b: ~a.overlap(b),
    FilterOperator.contains: lambda a, b: a.contains(b),
    FilterOperator.not_contains: lambda a, b: ~a.contains(b),
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


def _apply_filter(
    stmt: TSelectable,
    ns: EntityNamespace,
    field: str,
    op: FilterOperator,
    val: Any,
) -> TSelectable:
    try:
        cond = DEFAULT_FILTERS[op](ns[field], val)
    except KeyError:
        raise NotImplementedError(f"Operator {op} is not implemented")

    return cast(TSelectable, stmt.where(cond))


def apply_filters(
    stmt: TSelectable,
    filters: FilterValues,
) -> TSelectable:
    ns = _get_entity_namespace(stmt)

    for field, field_filters in filters.items():
        for op, val in field_filters.items():
            stmt = _apply_filter(stmt, ns, field, op, val)

    return stmt


def adapt_sqlalchemy_column_type(column: ColumnProperty) -> FilterFieldDef:
    expr: Any = column.expression

    type_: Any
    if isinstance(expr.type, ARRAY):
        type_ = List[expr.type.item_type.python_type]
    else:
        type_ = expr.type.python_type

    if expr.nullable:
        type_ = Optional[type_]

    return cast(FilterFieldDef, type_)


def create_filters_from_orm(
    obj: Any,
    *,
    in_: Optional[FilterPlace] = None,
    alias_generator: Optional[FilterAliasGenerator] = None,
    include_fk: bool = False,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
    **overrides: FilterFieldDef,
) -> FiltersResolver:
    inspected = inspect(obj, raiseerr=True)

    if include is None:
        include = {*inspected.mapper.attrs.keys()}
    if exclude is None:
        exclude = ()

    fields = {}
    for name, column in inspected.mapper.attrs.items():
        if name not in include or name in exclude:
            continue

        if not isinstance(column, ColumnProperty):
            continue

        if not include_fk and column.expression.foreign_keys:
            continue

        fields[name] = adapt_sqlalchemy_column_type(column)

    return create_filters(
        in_=in_,
        alias_generator=alias_generator,
        **{**fields, **overrides},
    )


__all__ = [
    "adapt_sqlalchemy_column_type",
    "apply_filters",
    "create_filters_from_orm",
]
