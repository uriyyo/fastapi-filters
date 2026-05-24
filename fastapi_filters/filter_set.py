import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    TypeVar,
    get_args,
    get_origin,
)

from fastapi import Depends
from pydantic import BaseModel, model_validator
from typing_extensions import Self, dataclass_transform

from .fields import FilterField
from .filters import FiltersCreateHooks, create_filters
from .op import FilterOp
from .types import AbstractFilterOperator, FiltersResolver, FilterValues

T_co = TypeVar("T_co", covariant=True)


@dataclass_transform(
    field_specifiers=(FilterField,),
)
class FilterSet(BaseModel):
    __filters__: ClassVar[dict[str, FilterField[Any]]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        filters: dict[str, FilterField[Any]] = {}
        for field_name, field_info in cls.model_fields.items():
            annotation = field_info.annotation

            if get_origin(annotation) is not FilterField:
                continue

            (elem_type,) = get_args(annotation) or (None,)
            spec = field_info.default if isinstance(field_info.default, FilterField) else None

            if spec is None:
                filter_field: FilterField[Any] = FilterField(
                    type=elem_type,
                    name=field_name,
                )
            else:
                filter_field = spec.replace(
                    type=spec.type if spec.type is not None else elem_type,
                    name=field_name,
                )

            filters[field_name] = filter_field

            # expose the field at the class var for the ``Cls.field == value`` DSL
            setattr(cls, field_name, filter_field)

        cls.__filters__ = filters
        cls.__signature__ = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="__values__",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(_filters_from_set(cls)),
                    annotation=FilterValues,
                )
            ],
            return_annotation=cls,
        )

    @model_validator(mode="before")
    @classmethod
    def _spread_values(cls, data: Any) -> Any:
        match data:
            case {"__values__": {**values}}:
                data = {**data, **values}

        return data

    def model_post_init(self, context: Any, /) -> None:
        for key in type(self).__filters__:
            match getattr(self, key, None):
                case None | FilterField():
                    object.__setattr__(self, key, {})

        self.init_filter_set()

    @classmethod
    def create(
        cls,
        **kwargs: Mapping[AbstractFilterOperator, Sequence[Any] | bool | Any],
    ) -> Self:
        return cls(**kwargs)

    def __bool__(self) -> bool:
        return bool(self.filter_values)

    def init_filter_set(self) -> None:
        pass

    @classmethod
    def from_ops(cls, *ops: FilterOp[Any]) -> Self:
        values: FilterValues = {k: {} for k in cls.__filters__}
        for op in ops:
            if op.operator in values[op.name]:
                raise ValueError(f"Duplicate operator {op.operator.name} for {op.name}")

            values[op.name][op.operator] = op.value

        return cls(**{k: v or None for k, v in values.items()})

    @classmethod
    def create_from_resolver(
        cls,
        resolver: FiltersResolver,
        *,
        name: str | None = None,
    ) -> type[Self]:
        anns = {k: FilterField[f.type] for k, f in resolver.__filters__.items()}  # type: ignore[name-defined]

        return type(
            name or "FilterSet",
            (cls,),
            {**resolver.__filters__, "__annotations__": anns},
        )

    @property
    def filter_values(self) -> FilterValues:
        return {key: val for key in self.__filters__ if (val := getattr(self, key))}

    def subset(self, *fields: FilterField[Any] | str) -> Self:
        names = {name for f in fields if (name := f.name if isinstance(f, FilterField) else f)}
        return self.create(
            **{k: v for k, v in self.filter_values.items() if k in names},
        )

    def extract(
        self,
        *fields: FilterField[Any] | str | type["FilterSet"],
        strict: bool = False,
    ) -> Self:
        names = set()
        for f in fields:
            if isinstance(f, FilterField):
                assert f.name is not None, "FilterField name is not set"
                names.add(f.name)
            elif isinstance(f, type) and issubclass(f, FilterSet):
                names |= f.__filters__.keys()
            else:
                names.add(f)

        if not strict:
            names &= self.filter_values.keys()

        attrs = {}
        for name in names:
            if val := getattr(self, name):
                attrs[name] = {**val}
                val.clear()

        return self.create(**attrs)

    @classmethod
    def __filter_field_adapt_type__(
        cls,
        field: FilterField[Any],
        tp: type[Any],
        op: AbstractFilterOperator,
    ) -> Any | None:
        return None

    @classmethod
    def __filter_field_generate_alias__(
        cls,
        name: str,
        op: AbstractFilterOperator,
        alias: str | None = None,
    ) -> str | None:
        return None


@dataclass
class _FitlerSetFiltersCreateHooks(FiltersCreateHooks):
    filter_set_cls: type[FilterSet]

    def filter_field_adapt_type(
        self,
        field: FilterField[Any],
        tp: type[Any],
        op: AbstractFilterOperator,
    ) -> Any:
        adapted = self.filter_set_cls.__filter_field_adapt_type__(field, tp, op)

        if adapted is not None:
            return adapted

        return super().filter_field_adapt_type(field, tp, op)

    def filter_field_generate_alias(
        self,
        name: str,
        op: AbstractFilterOperator,
        alias: str | None = None,
    ) -> str:
        generated = self.filter_set_cls.__filter_field_generate_alias__(name, op, alias)

        if generated is not None:
            return generated

        return super().filter_field_generate_alias(name, op, alias)


TFiltersSet = TypeVar("TFiltersSet", bound=FilterSet)


def _filters_from_set(
    filters_set: type[TFiltersSet],
) -> FiltersResolver:
    return create_filters(
        **{k: v for k, v in filters_set.__filters__.items() if not v.internal},  # type: ignore[arg-type]
        hooks=_FitlerSetFiltersCreateHooks(filters_set),
    )


def create_filters_from_set(
    filters_set: type[TFiltersSet],
) -> Callable[..., Awaitable[TFiltersSet]]:
    filters_dep = _filters_from_set(filters_set)

    async def resolver(values: FilterValues = Depends(filters_dep)) -> TFiltersSet:
        return filters_set.create(**values)

    for attr in ("__filters__", "__model__", "__defs__"):
        setattr(resolver, attr, getattr(filters_dep, attr))

    return resolver


__all__ = [
    "FilterSet",
    "create_filters_from_set",
]
