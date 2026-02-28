import operator
from collections.abc import Callable, Container, Iterator, Mapping
from contextlib import suppress
from typing import (
    Any,
    TypeAlias,
    TypeVar,
    cast,
)

from sqlalchemy import (
    ARRAY,
    ColumnExpressionArgument,
    asc,
    desc,
    inspect,
    nulls_first,
    nulls_last,
)
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.sql.selectable import Select

from fastapi_filters import FilterField, create_filters
from fastapi_filters.config import ConfigVar
from fastapi_filters.filter_set import FilterSet
from fastapi_filters.filters import FiltersCreateHooks
from fastapi_filters.operators import FilterOperator
from fastapi_filters.sorters import create_sorting
from fastapi_filters.types import (
    AbstractFilterOperator,
    FilterAliasGenerator,
    FilterFieldDef,
    FilterPlace,
    FiltersResolver,
    FilterValues,
    SortingDirection,
    SortingNulls,
    SortingResolver,
    SortingValues,
)
from fastapi_filters.utils import fields_include_exclude

TSelectable = TypeVar("TSelectable", bound=Select[Any])


def _overlap(a: Any, b: Any) -> Any:
    try:
        return a.overlap(b)
    except AttributeError:
        return a.overlaps(b)


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
    FilterOperator.overlap: lambda a, b: _overlap(a, b),  # noqa: PLW0108
    FilterOperator.not_overlap: lambda a, b: ~_overlap(a, b),
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
    tuple[SortingDirection, SortingNulls],
    Callable[[ColumnExpressionArgument[Any]], ColumnExpressionArgument[Any]],
] = {
    ("asc", "bigger"): nulls_last,
    ("asc", "smaller"): nulls_first,
    ("desc", "bigger"): nulls_first,
    ("desc", "smaller"): nulls_last,
}

EntityNamespace: TypeAlias = Mapping[str, Any]
AdditionalNamespace: TypeAlias = Mapping[str | FilterField[Any], Any]


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


def _normalize_additional_namespace(additional: AdditionalNamespace) -> EntityNamespace:
    ns = {}
    for key, value in additional.items():
        k = key.name if isinstance(key, FilterField) else key
        assert k, "Additional namespace key cannot be empty"

        ns[k] = value

    return ns


def _default_hook(*_: Any) -> Any:
    raise NotImplementedError


ApplyFilterFunc: TypeAlias = Callable[
    [TSelectable, EntityNamespace, str, AbstractFilterOperator, Any],
    TSelectable,
]
AddFilterConditionFunc: TypeAlias = Callable[[TSelectable, str, Any], TSelectable]

custom_apply_filter: ConfigVar[ApplyFilterFunc[Any]] = ConfigVar(
    "apply_filter",
    default=_default_hook,
)
custom_add_condition: ConfigVar[AddFilterConditionFunc[Any]] = ConfigVar(
    "add_condition",
    default=_default_hook,
)


def generic_condition(left: Any, right: Any, op: AbstractFilterOperator) -> Any:
    return DEFAULT_FILTERS[op](left, right)


def _apply_filter(
    stmt: TSelectable,
    ns: EntityNamespace,
    field: str,
    op: AbstractFilterOperator,
    val: Any,
    apply_filter: ApplyFilterFunc[TSelectable] | None = None,
    add_condition: AddFilterConditionFunc[TSelectable] | None = None,
) -> TSelectable:
    custom_apply_filter_impl = custom_apply_filter.get()

    try:
        cond = None
        if apply_filter:
            try:
                cond = apply_filter(stmt, ns, field, op, val)
                assert cond is not None
            except (NotImplementedError, AssertionError):
                pass

        if cond is None:
            cond = custom_apply_filter_impl(stmt, ns, field, op, val)
            assert cond is not None
    except (NotImplementedError, AssertionError):
        if field not in ns:
            raise ValueError(f"Unknown field {field}") from None

        try:
            cond = generic_condition(ns[field], val, op)
        except KeyError:
            raise NotImplementedError(f"Operator {op} is not implemented") from None

    if add_condition:
        try:
            return add_condition(stmt, field, cond)
        except NotImplementedError:
            pass

    global_add_condition = custom_add_condition.get()

    try:
        res = global_add_condition(stmt, field, cond)
        assert res is not None

        return cast(TSelectable, res)
    except (NotImplementedError, AssertionError):
        pass

    return stmt.where(cond)  # type: ignore[arg-type]


def apply_filters(
    stmt: TSelectable,
    filters: FilterValues | FilterSet,
    *,
    remapping: Mapping[str, str] | None = None,
    additional: AdditionalNamespace | None = None,
    apply_filter: ApplyFilterFunc[TSelectable] | None = None,
    add_condition: AddFilterConditionFunc[TSelectable] | None = None,
) -> TSelectable:
    if isinstance(filters, FilterSet):
        filters = filters.filter_values

    remapping = remapping or {}
    ns = {
        **_get_entity_namespace(stmt),
        **_normalize_additional_namespace(additional or {}),
    }

    for field, field_filters in filters.items():
        field = remapping.get(field, field)

        for op, val in field_filters.items():
            stmt = _apply_filter(stmt, ns, field, op, val, apply_filter, add_condition)

    return stmt


def apply_sorting(
    stmt: TSelectable,
    sorting: SortingValues,
    *,
    remapping: Mapping[str, str] | None = None,
    additional: AdditionalNamespace | None = None,
) -> TSelectable:
    remapping = remapping or {}
    ns = {
        **_get_entity_namespace(stmt),
        **_normalize_additional_namespace(additional or {}),
    }

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
    filters: FilterValues | FilterSet,
    sorting: SortingValues,
    *,
    remapping: Mapping[str, str] | None = None,
    additional: AdditionalNamespace | None = None,
    apply_filter: ApplyFilterFunc[TSelectable] | None = None,
    add_condition: AddFilterConditionFunc[TSelectable] | None = None,
) -> TSelectable:
    stmt = apply_filters(
        stmt,
        filters,
        remapping=remapping,
        additional=additional,
        apply_filter=apply_filter,
        add_condition=add_condition,
    )
    return apply_sorting(
        stmt,
        sorting,
        remapping=remapping,
        additional=additional,
    )


def adapt_sqlalchemy_column_type(column: ColumnProperty[Any]) -> FilterFieldDef:
    expr: Any = column.expression

    type_: Any
    type_ = list[expr.type.item_type.python_type] if isinstance(expr.type, ARRAY) else expr.type.python_type

    if expr.nullable:
        type_ = type_ | None

    return cast(FilterFieldDef, type_)


def _iter_over_orm_columns(
    obj: Any,
    *,
    include_fk: bool = False,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
    remapping: Mapping[str, str] | None = None,
) -> Iterator[tuple[str, ColumnProperty[Any]]]:
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
    in_: FilterPlace | None = None,
    alias_generator: FilterAliasGenerator | None = None,
    include_fk: bool = False,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
    remapping: Mapping[str, str] | None = None,
    hooks: FiltersCreateHooks | None = None,
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
        hooks=hooks,
        **{**fields, **overrides},
    )


def create_sorting_from_orm(
    obj: Any,
    *,
    default: str | None = None,
    in_: FilterPlace | None = None,
    include_fk: bool = False,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
    remapping: Mapping[str, str] | None = None,
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
    "adapt_sqlalchemy_column_type",
    "apply_filters",
    "apply_filters_and_sorting",
    "apply_sorting",
    "create_filters_from_orm",
    "create_sorting_from_orm",
    "custom_add_condition",
    "custom_apply_filter",
    "generic_condition",
]
