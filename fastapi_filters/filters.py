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
from pydantic.fields import FieldInfo
from typing_extensions import Annotated

from .config import ConfigVar
from .schemas import CSVList
from .operators import FilterOperator
from .types import (
    FilterValues,
    FiltersResolver,
    FilterAliasGenerator,
    FilterFieldDef,
    FilterPlace,
    AbstractFilterOperator,
)
from .utils import async_safe, is_seq, unwrap_seq_type, fields_include_exclude
from .fields import FilterField


def default_alias_generator(name: str, op: AbstractFilterOperator) -> str:
    return f"{name}[{op.name.rstrip('_')}]"


alias_generator_config: ConfigVar[FilterAliasGenerator] = ConfigVar(
    "alias_generator",
    default=default_alias_generator,
)


def adapt_type(tp: Type[Any], op: AbstractFilterOperator) -> Any:
    if is_seq(tp):
        return CSVList[unwrap_seq_type(tp)]  # type: ignore

    if op in {FilterOperator.like, FilterOperator.ilike, FilterOperator.not_like, FilterOperator.not_ilike}:
        return str

    if op == FilterOperator.is_null:
        return bool

    if op in {FilterOperator.in_, FilterOperator.not_in}:
        return CSVList[tp]  # type: ignore

    return tp


def field_filter_to_raw_fields(
    name: str,
    field: FilterField[Any],
    alias_generator: Optional[FilterAliasGenerator] = None,
) -> Iterator[Tuple[str, Any, AbstractFilterOperator, Optional[str]]]:
    if alias_generator is None:
        alias_generator = alias_generator_config.get()

    yield name, field.type, cast(AbstractFilterOperator, field.default_op), None

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
    checker = fields_include_exclude(model.model_fields, include, exclude)

    def _get_type(f: FieldInfo) -> Any:
        if f.metadata:
            return Annotated[tuple([f.annotation, *f.metadata])]

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

    fields: Dict[str, FilterField[Any]] = {
        name: f_def if isinstance(f_def, FilterField) else FilterField(f_def) for name, f_def in kwargs.items()
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
            (
                fname,
                new_tp := adapt_type(tp, op),
                dataclass_field(default=in_(None, alias=alias, annotation=new_tp)),
            )
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
    _get_filters.__filters__ = fields  # type: ignore[attr-defined]

    return cast(FiltersResolver, _get_filters)


__all__ = [
    "alias_generator_config",
    "create_filters",
    "create_filters_from_model",
]
