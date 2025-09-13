from collections.abc import Container
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
)

from fastapi import Depends
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .fields import FilterField
from .filterset import FilterSet, create_filters_from_set
from .types import (
    AbstractFilterOperator,
    FilterAliasGenerator,
    FilterFieldDef,
    FilterPlace,
    FiltersResolver,
    FilterValues,
)
from .utils import copy_filter_resolver_metadata, fields_include_exclude


def create_filters_from_model(
    model: type[BaseModel],
    *,
    in_: FilterPlace | None = None,
    alias_generator: FilterAliasGenerator | None = None,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
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
    in_: FilterPlace | None = None,
    alias_generator: FilterAliasGenerator | None = None,
    **kwargs: FilterFieldDef,
) -> FiltersResolver:
    fields: dict[str, FilterField[Any]] = {
        name: f_def if isinstance(f_def, FilterField) else FilterField(f_def) for name, f_def in kwargs.items()
    }

    if TYPE_CHECKING:
        from .filterset import FilterSet as _Cls
    else:
        _Cls = type(
            "FilterSet",
            (FilterSet,),
            {
                **fields,
                "__annotations__": fields,
            },
        )

    class _FilterSet(_Cls):
        @classmethod
        def generate_filter_field_alias(
            cls,
            field: FilterField[Any],
            op: AbstractFilterOperator,
            alias: str | None = None,
        ) -> str:
            if alias_generator is not None:
                return alias_generator(field.name, op, alias)  # type: ignore[arg-type]

            return super().generate_filter_field_alias(field, op, alias)

    _filterset_resolver = create_filters_from_set(_FilterSet, in_=in_)

    async def _resolver(
        filterset: Annotated[FilterSet, Depends(_filterset_resolver)],
    ) -> FilterValues:
        return filterset.filter_values

    copy_filter_resolver_metadata(_resolver, _filterset_resolver)
    return _resolver  # type: ignore[return-value]


__all__ = [
    "create_filters",
    "create_filters_from_model",
]
