import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import InitVar, asdict, dataclass, replace
from typing import (
    Any,
    ClassVar,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from fastapi import Depends
from typing_extensions import Self, dataclass_transform

from .fields import FilterField
from .filters import create_filters
from .op import FilterOp
from .types import AbstractFilterOperator, FiltersResolver, FilterValues

T_co = TypeVar("T_co", covariant=True)


class FilterSetMeta(type):
    def __init__(
        cls,
        name: str,
        bases: Any,
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        super().__init__(name, bases, namespace, **kwargs)

        hints = get_type_hints(cls, include_extras=True)
        specs = {key: get_args(value)[0] for key, value in hints.items() if get_origin(value) is FilterField}

        cls.__filters__: dict[str, FilterField[Any]] = {}
        for base in bases:
            cls.__filters__.update(getattr(base, "__filters__", {}))

        for key, value in specs.items():
            try:
                filter_field = getattr(cls, key)
            except AttributeError:
                filter_field = FilterField(value)
                setattr(cls, key, filter_field)

            if filter_field.type is None:
                filter_field = replace(filter_field, type=value)

            filter_field.__set_name__(cls, key)
            cls.__filters__[key] = filter_field

        for key in cls.__filters__:  # used to add default value for dataclass
            setattr(cls, key, None)

        d_cls = dataclass(
            cast(type[Any], cls),
            kw_only=True,
        )

        for key, value in cls.__filters__.items():
            setattr(d_cls, key, value)

        try:
            _ = FilterSet
        except NameError:
            return

        d_cls.__signature__ = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="__values__",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(_filters_from_set(d_cls)),
                    annotation=FilterValues,
                )
            ],
            return_annotation=FilterSet,
        )


@dataclass_transform(
    field_specifiers=(FilterField,),
)
class FilterSet(metaclass=FilterSetMeta):
    __values__: InitVar[FilterValues | None] = None  # type: ignore[assignment]

    __filters__: ClassVar[dict[str, FilterField[Any]]]

    @classmethod
    def create(
        cls,
        **kwargs: Mapping[AbstractFilterOperator, Sequence[Any] | bool | Any],
    ) -> Self:
        return cls(**kwargs)

    def __post_init__(
        self,
        __values__: FilterValues | None,
    ) -> None:
        for key, value in (__values__ or {}).items():
            setattr(self, key, value)

        for key in asdict(self):  # type: ignore[call-overload]
            # auto replace uninitialized fields with empty dict
            if getattr(self, key) is None:
                setattr(self, key, {})

        self.init_filter_set()

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


TFiltersSet = TypeVar("TFiltersSet", bound=FilterSet)


def _filters_from_set(
    filters_set: type[TFiltersSet],
) -> FiltersResolver:
    return create_filters(
        **{k: v for k, v in filters_set.__filters__.items() if not v.internal},  # type: ignore[arg-type]
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
