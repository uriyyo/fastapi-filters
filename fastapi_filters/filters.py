from collections import defaultdict
from collections.abc import Container, Iterator
from dataclasses import asdict, make_dataclass
from typing import (
    Annotated,
    Any,
    Optional,
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


def default_alias_generator(
    name: str,
    op: AbstractFilterOperator,
    alias: Optional[str] = None,
) -> str:
    name = alias or name
    return f"{name}[{op.name.rstrip('_')}]"


alias_generator_config: ConfigVar[FilterAliasGenerator] = ConfigVar(
    "alias_generator",
    default=default_alias_generator,
)


def adapt_type(
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


def field_filter_to_raw_fields(
    name: str,
    field: FilterField[Any],
    alias_generator: Optional[FilterAliasGenerator] = None,
) -> Iterator[tuple[str, Any, AbstractFilterOperator, Optional[str]]]:
    if alias_generator is None:
        alias_generator = alias_generator_config.get()

    yield name, field.type, cast(AbstractFilterOperator, field.default_op), field.alias

    for op in field.operators or ():
        yield (
            f"{name}__{op.name}",
            field.type,
            op,
            alias_generator(
                name,
                op,
                field.alias,
            ),
        )


def create_filters_from_model(
    model: type[BaseModel],
    *,
    in_: Optional[FilterPlace] = None,
    alias_generator: Optional[FilterAliasGenerator] = None,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
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
        **{
            **{name: _get_type(field) for name, field in model.model_fields.items() if checker(name)},
            **(overrides or {}),
        },
    )


def create_filters(
    *,
    in_: Optional[FilterPlace] = None,
    alias_generator: Optional[FilterAliasGenerator] = None,
    **kwargs: FilterFieldDef,
) -> FiltersResolver:
    if in_ is None:
        in_ = Query

    fields: dict[str, FilterField[Any]] = {
        name: f_def if isinstance(f_def, FilterField) else FilterField(f_def) for name, f_def in kwargs.items()
    }

    fields_defs = [
        (name, fname, field, tp, alias, op)
        for name, field in fields.items()
        for fname, tp, op, alias in field_filter_to_raw_fields(
            name,
            field,
            alias_generator,
        )
    ]

    defs = {fname: (name, op) for name, fname, *_, op in fields_defs}

    filter_model = make_dataclass(
        "Filters",
        [
            (
                fname,
                Annotated[adapt_type(field, tp, op), in_(alias=alias)],
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
    "alias_generator_config",
    "create_filters",
    "create_filters_from_model",
]
