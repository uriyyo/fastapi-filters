from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from typing import (
    TypeVar,
    Any,
    List,
    Optional,
    Callable,
    Awaitable,
    get_args,
    Dict,
    ClassVar,
    Type,
)

from fastapi import Depends
from typing_extensions import dataclass_transform, Self, get_type_hints, get_origin

from .fields import FilterField
from .filters import create_filters
from .op import FilterOp
from .types import AbstractFilterOperator, FilterValues, FiltersResolver

T = TypeVar("T", covariant=True)


class FilterSetMeta(type):
    def __init__(cls, name: str, bases: Any, namespace: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(name, bases, namespace, **kwargs)

        hints = get_type_hints(cls)
        specs = {key: get_args(value)[0] for key, value in hints.items() if get_origin(value) is FilterField}

        cls.__filter_specs__: Dict[str, FilterField[Any]] = {}
        for base in bases:
            cls.__filter_specs__.update(getattr(base, "__filter_specs__", {}))

        for key, value in specs.items():
            try:
                filter_field = getattr(cls, key)
            except AttributeError:
                filter_field = FilterField(value)
                setattr(cls, key, filter_field)

            if filter_field.type is None:
                filter_field = replace(filter_field, type=value)

            filter_field.__set_name__(cls, key)
            cls.__filter_specs__[key] = filter_field

        d_cls = dataclass(cls)  # type: ignore
        for key, value in cls.__filter_specs__.items():
            setattr(d_cls, key, value)


@dataclass_transform(
    field_specifiers=(FilterField,),
)
class FilterSet(metaclass=FilterSetMeta):
    __filter_specs__: ClassVar[Dict[str, FilterField[Any]]]

    def __post_init__(self) -> None:
        if any(isinstance(val, FilterField) for val in asdict(self).values()):  # type: ignore
            raise TypeError("Filter values incorrectly initialized")

    @classmethod
    def from_ops(cls, *ops: FilterOp) -> Self:
        values: FilterValues = {k: {} for k in cls.__filter_specs__}
        for op in ops:
            if op.operator in values[op.name]:
                raise ValueError(f"Duplicate operator {op.operator} for {op.name}")

            values[op.name][op.operator] = op.value

        return cls(**{k: v or None for k, v in values.items()})

    @classmethod
    def create_from_resolver(
        cls,
        resolver: FiltersResolver,
        *,
        name: Optional[str] = None,
    ) -> Type[Self]:
        anns = {k: FilterField[f.type] for k, f in resolver.__filters__.items()}  # type: ignore[name-defined]

        return type(name or "FilterSet", (cls,), {**resolver.__filters__, "__annotations__": anns})

    @property
    def filter_values(self) -> FilterValues:
        return {key: val for key in self.__filter_specs__ if (val := getattr(self, key))}

    def remove_op(self, field: str, operators: Optional[List[AbstractFilterOperator]] = None) -> Self:
        if not operators:
            setattr(self, field, None)
            return self

        for operator in operators:
            del getattr(self, field)[operator]

        if not getattr(self, field):
            setattr(self, field, None)

        return self

    def has_op(self, field: str, operator: AbstractFilterOperator) -> bool:
        return operator in (getattr(self, field, None) or {})


TFiltersSet = TypeVar("TFiltersSet", bound=FilterSet)


def create_filters_from_set(filters_set: Type[TFiltersSet]) -> Callable[..., Awaitable[TFiltersSet]]:
    filters_dep = create_filters(**filters_set.__filter_specs__)  # type: ignore

    async def resolver(values: FilterValues = Depends(filters_dep)) -> TFiltersSet:
        return filters_set(**{**dict.fromkeys(filters_set.__filter_specs__, None), **values})

    return resolver


__all__ = [
    "FilterSet",
    "create_filters_from_set",
]
