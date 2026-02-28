from collections import defaultdict
from collections.abc import Callable, Container, Iterator
from contextlib import ExitStack
from dataclasses import asdict, dataclass, make_dataclass
from typing import (
    Annotated,
    Any,
    cast,
)

from fastapi import Depends, Query
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .config import ConfigVar
from .fields import FilterField
from .operators import FilterOperator
from .schemas import CSVList
from .types import (
    AbstractFilterOperator,
    FilterAliasGenerator,
    FilterFieldDef,
    FilterPlace,
    FiltersResolver,
    FilterValues,
)
from .utils import async_safe, fields_include_exclude, is_seq, unwrap_seq_type

alias_generator_config: ConfigVar[FilterAliasGenerator | None] = ConfigVar(
    "alias_generator",
    default=None,
)


@dataclass
class FiltersCreateHooks:
    def filter_field_generate_alias(
        self,
        name: str,
        op: AbstractFilterOperator,
        alias: str | None = None,
    ) -> str:
        # TODO: to many places to do simple things
        if override := alias_generator_config.get():
            return override(name, op, alias)

        name = alias or name
        return f"{name}[{op.name.rstrip('_')}]"

    def filter_field_adapt_type(
        self,
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

    def filter_field_to_raw_fields(
        self,
        name: str,
        field: FilterField[Any],
    ) -> Iterator[tuple[str, Any, AbstractFilterOperator, str | None]]:
        yield name, field.type, cast(AbstractFilterOperator, field.default_op), field.alias

        for op in field.operators or ():
            yield (
                f"{name}__{op.name}",
                field.type,
                op,
                self.filter_field_generate_alias(name, op, field.alias),
            )


filters_create_hooks_factory_config: ConfigVar[Callable[[], FiltersCreateHooks]] = ConfigVar(
    "filters_create_hooks_factory",
    default=FiltersCreateHooks,
)


def create_filters_from_model(
    model: type[BaseModel],
    *,
    in_: FilterPlace | None = None,
    alias_generator: FilterAliasGenerator | None = None,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
    hooks: FiltersCreateHooks | None = None,
    **overrides: FilterFieldDef,
) -> FiltersResolver:
    checker = fields_include_exclude(model.model_fields, include, exclude)

    def _get_type(f: FieldInfo) -> Any:
        if f.metadata:
            return Annotated[(f.annotation, *f.metadata)]

        return f.annotation

    return create_filters(
        in_=in_,
        alias_generator=alias_generator,
        hooks=hooks,
        **{
            **{name: _get_type(field) for name, field in model.model_fields.items() if checker(name)},
            **(overrides or {}),
        },
    )


def create_filters(
    *,
    in_: FilterPlace | None = None,
    alias_generator: FilterAliasGenerator | None = None,
    hooks: FiltersCreateHooks | None = None,
    **kwargs: FilterFieldDef,
) -> FiltersResolver:
    if in_ is None:
        in_ = Query

    hooks = hooks or FiltersCreateHooks()

    fields: dict[str, FilterField[Any]] = {
        name: f_def if isinstance(f_def, FilterField) else FilterField(f_def) for name, f_def in kwargs.items()
    }

    with ExitStack() as stack:
        # TODO: maybe better to remove ConvigVar? To many ways to do the same thing
        if alias_generator:
            stack.enter_context(alias_generator_config.set(alias_generator))

        fields_defs = [
            (name, fname, field, tp, alias, op)
            for name, field in fields.items()
            for fname, tp, op, alias in hooks.filter_field_to_raw_fields(
                name,
                field,
            )
        ]

    defs = {fname: (name, op) for name, fname, *_, op in fields_defs}

    filter_model = make_dataclass(
        "Filters",
        [
            (
                fname,
                Annotated[
                    hooks.filter_field_adapt_type(field, tp, op),
                    in_(alias=alias),
                ],
                None,
            )
            for _, fname, field, tp, alias, op in fields_defs
        ],
    )

    async def _get_filters(f: Any = Depends(async_safe(filter_model))) -> FilterValues:
        values: FilterValues = defaultdict(dict)

        for key, value in asdict(f).items():
            if value is not None:
                name, op = defs[key]
                values[name][op] = value

        return {**values}

    _get_filters.__model__ = filter_model  # type: ignore[attr-defined]
    _get_filters.__defs__ = defs  # type: ignore[attr-defined]
    _get_filters.__filters__ = fields  # type: ignore[attr-defined]

    return cast(FiltersResolver, _get_filters)


__all__ = [
    "FiltersCreateHooks",
    "alias_generator_config",
    "create_filters",
    "create_filters_from_model",
]
