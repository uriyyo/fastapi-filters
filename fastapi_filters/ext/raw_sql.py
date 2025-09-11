import re
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache, cached_property
from typing import TYPE_CHECKING, Any, NamedTuple, TypeAlias, cast

from sqlalchemy import Dialect, column, make_url, select
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.compiler import StrSQLCompiler
from sqlalchemy.sql.type_api import TypeEngine

from fastapi_filters import FilterSet, FilterValues
from fastapi_filters.config import ConfigVar
from fastapi_filters.types import SortingValues

from .sqlalchemy import DEFAULT_FILTERS, SORT_FUNCS, SORT_NULLS_FUNCS

_Dialect: TypeAlias = str | None
_SQLType: TypeAlias = TypeEngine[Any] | type[TypeEngine[Any]]

default_dialect: ConfigVar[_Dialect] = ConfigVar(
    name="default_dialect",
    default=None,
)
default_compile_kwargs: ConfigVar[_Dialect] = ConfigVar(
    name="default_compile_kwargs",
    default=None,
)


@cache
def _get_dialect(dialect: str) -> Dialect:
    return make_url(f"{dialect}://").get_dialect()()


if TYPE_CHECKING:

    class _BaseCompiledStatement(NamedTuple):
        stmt: str
        args: tuple[Any, ...]
else:

    class _BaseCompiledStatement:
        stmt: str
        args: tuple[Any, ...]

        def __getitem__(self, item):
            if item == 0:
                return self.stmt
            if item == 1:
                return self.args

            raise IndexError("Index out of range for CompiledStatement")

        def __len__(self):
            return 2


def _adjust_args_pos_in_statement(
    num_char: str,
    stmt: str,
    arg_start: int,
) -> str:
    regex = re.compile(rf"\{num_char}(\d+)")

    return regex.sub(
        lambda match: f"{num_char}{int(match.group(1)) + arg_start - 1}",
        stmt,
    )


@dataclass(kw_only=True)
class CompiledStatement(_BaseCompiledStatement):
    arg_start: int = 1
    _compiled: StrSQLCompiler

    @property
    def start(self) -> int:
        return self.arg_start + self.end - len(self.args)

    @property
    def end(self) -> int:
        return self.arg_start + len(self.args)

    @property
    def nargs(self) -> int:
        return len(self.args)

    @cached_property
    def stmt(self) -> str:
        if self.is_positional and self.arg_start != 1:
            return _adjust_args_pos_in_statement(
                num_char=self._compiled._numeric_binds_identifier_char,
                stmt=self._compiled.string,
                arg_start=self.arg_start,
            )

        return self._compiled.string

    @property
    def is_positional(self) -> bool:
        return self._compiled.positional

    @property
    def args(self) -> tuple[Any, ...]:
        params = self._compiled.params

        if self.is_positional:
            return tuple(params[name] for name in self._compiled.positiontup or ())

        return tuple(params.values())

    @property
    def params(self) -> Mapping[str, Any]:
        return cast(Mapping[str, Any], self._compiled.params)


def _compile_sql(
    stmt: ClauseElement,
    *,
    dialect: _Dialect | None = None,
    arg_start: int | None = None,
) -> CompiledStatement:
    dialect = dialect or default_dialect.get()
    sa_dialect: Dialect | None = _get_dialect(dialect) if dialect else None

    if arg_start is None:
        arg_start = 1

    compiled = stmt.compile(
        dialect=sa_dialect,
        compile_kwargs=default_compile_kwargs.get() or {},
    )

    return CompiledStatement(
        arg_start=arg_start,
        _compiled=cast(StrSQLCompiler, compiled),
    )


def apply_filters(
    filters: FilterValues | FilterSet,
    *,
    remapping: Mapping[str, str] | None = None,
    types: Mapping[str, _SQLType] | None = None,
    dialect: _Dialect | None = None,
    arg_start: int | None = None,
) -> CompiledStatement | None:
    types = types or {}
    remapping = remapping or {}
    if isinstance(filters, FilterSet):
        filters = filters.filter_values

    if not filters:
        return None

    stmt = select(1)
    for field, field_filters in filters.items():
        field = remapping.get(field, field)

        for op, val in field_filters.items():
            if (cond := DEFAULT_FILTERS.get(op)) is not None:
                col = column(field, type_=types.get(field))
                stmt = stmt.where(cond(col, val))
            else:
                raise NotImplementedError(f"Operator {op} is not implemented")

    return _compile_sql(
        cast(ClauseElement, stmt.whereclause),
        dialect=dialect,
        arg_start=arg_start,
    )


def apply_sorting(
    sorting: SortingValues,
    *,
    remapping: Mapping[str, str] | None = None,
    dialect: _Dialect | None = None,
    types: Mapping[str, _SQLType] | None = None,
    arg_start: int | None = None,
) -> CompiledStatement | None:
    types = types or {}
    remapping = remapping or {}

    if not sorting:
        return None

    stmt = select(1)
    for field, direction, nulls in sorting:
        field = remapping.get(field, field)
        col = column(field, type_=types.get(field))

        if sort_func := SORT_FUNCS.get(direction):
            sort_expr = sort_func(col)

            if nulls is not None:
                sort_expr = SORT_NULLS_FUNCS[(direction, nulls)](sort_expr)

            stmt = stmt.order_by(sort_expr)
        else:
            raise ValueError(f"Unknown sorting direction {direction}")

    return _compile_sql(
        stmt._order_by_clause,
        dialect=dialect,
        arg_start=arg_start,
    )


def apply_filters_and_sorting(
    filters: FilterValues | FilterSet,
    sorting: SortingValues,
    *,
    dialect: _Dialect | None = None,
    remapping: Mapping[str, str] | None = None,
    types: Mapping[str, _SQLType] | None = None,
    arg_start: int | None = None,
) -> tuple[CompiledStatement | None, CompiledStatement | None]:
    filters_res = apply_filters(
        filters,
        arg_start=arg_start,
        remapping=remapping,
        types=types,
        dialect=dialect,
    )

    if filters_res and filters_res.is_positional:
        arg_start = filters_res.end

    sorting_res = apply_sorting(
        sorting,
        arg_start=arg_start,
        remapping=remapping,
        types=types,
        dialect=dialect,
    )

    return filters_res, sorting_res


__all__ = [
    "CompiledStatement",
    "apply_filters",
    "apply_filters_and_sorting",
    "apply_sorting",
    "default_compile_kwargs",
    "default_dialect",
]
