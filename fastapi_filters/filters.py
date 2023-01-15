from collections import defaultdict
from dataclasses import asdict, make_dataclass
from dataclasses import field as dataclass_field
from typing import (
    Any,
    Iterator,
    cast,
    Dict,
    Tuple,
    Optional,
    Type,
    Container,
)

from fastapi import Query, Depends
from pydantic import BaseModel

from .schemas import CSVList
from .operators import FilterOperator
from .types import FilterValues, FiltersResolver, FilterAliasGenerator, FilterFieldDef, FilterPlace
from .utils import async_safe, is_seq, unwrap_seq_type
from .fields import FieldFilter


def adapt_type(tp: Type[Any], op: FilterOperator) -> Any:
    if is_seq(tp):
        return CSVList[unwrap_seq_type(tp)]  # type: ignore

    if op == FilterOperator.is_null:
        return bool

    if op in {FilterOperator.in_, FilterOperator.not_in}:
        return CSVList[tp]  # type: ignore

    return tp


def default_alias_generator(name: str, op: FilterOperator) -> str:
    return f"{name}[{op.name.rstrip('_')}]"


def field_filter_to_raw_fields(
    name: str,
    field: FieldFilter,
    alias_generator: Optional[FilterAliasGenerator] = None,
) -> Iterator[Tuple[str, Any, FilterOperator, Optional[str]]]:
    if alias_generator is None:
        alias_generator = default_alias_generator

    yield name, field.type, cast(FilterOperator, field.default_op), None

    for op in field.operators or ():
        yield f"{name}__{op.name}", field.type, op, alias_generator(name, op)


def create_filters_from_model(
    model: Type[BaseModel],
    *,
    in_: Optional[FilterPlace] = None,
    alias_generator: Optional[FilterAliasGenerator] = None,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
    **overrides: FilterFieldDef,
) -> FiltersResolver:
    if include is None:
        include = {*model.__fields__}
    if exclude is None:
        exclude = ()

    return create_filters(
        in_=in_,
        alias_generator=alias_generator,
        **{
            **{
                name: field.outer_type_
                for name, field in model.__fields__.items()
                if name in include and name not in exclude
            },
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

    fields: Dict[str, FieldFilter] = {
        name: f_def if isinstance(f_def, FieldFilter) else FieldFilter(f_def) for name, f_def in kwargs.items()
    }

    fields_defs = [
        (name, fname, tp, alias, op)
        for name, field in fields.items()
        for fname, tp, op, alias in field_filter_to_raw_fields(name, field, alias_generator)
    ]

    defs = {fname: (name, op) for name, fname, _, _, op in fields_defs}

    filter_model = make_dataclass(
        "Filters",
        [
            (fname, adapt_type(tp, op), dataclass_field(default=in_(None, alias=alias)))
            for _, fname, tp, alias, op in fields_defs
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

    return cast(FiltersResolver, _get_filters)


__all__ = [
    "FieldFilter",
    "create_filters",
    "create_filters_from_model",
]
