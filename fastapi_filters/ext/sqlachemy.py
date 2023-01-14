import operator
from contextlib import suppress
from typing import TypeVar, Mapping, Any, Callable, cast

from sqlalchemy.sql.selectable import Select
from typing_extensions import TypeAlias

from fastapi_filters.operators import Operators
from fastapi_filters.types import FilterValues

TSelectable = TypeVar("TSelectable", bound=Select)


DEFAULT_FILTERS: Mapping[Operators, Callable[[Any, Any], Any]] = {
    Operators.eq: operator.eq,
    Operators.ne: operator.ne,
    Operators.gt: operator.gt,
    Operators.ge: operator.ge,
    Operators.lt: operator.lt,
    Operators.le: operator.le,
    Operators.in_: lambda a, b: a.in_(b),
    Operators.not_in: lambda a, b: a.not_in(b),
    Operators.is_null: lambda a, b: a.is_(None) if b else a.isnot(None),
    Operators.ov: lambda a, b: a.overlap(b),
    Operators.not_ov: lambda a, b: ~a.overlap(b),
    Operators.contains: lambda a, b: a.contains(b),
    Operators.not_contains: lambda a, b: ~a.contains(b),
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
    op: Operators,
    val: Any,
) -> TSelectable:
    cond = DEFAULT_FILTERS[op](ns[field], val)

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


__all__ = [
    "apply_filters",
]
