from dataclasses import dataclass, asdict, replace
from typing import (
    TypeVar,
    TYPE_CHECKING,
    overload,
    Any,
    Union,
    List,
    Optional,
    Callable,
    Awaitable,
    Mapping,
    get_args,
    Dict,
    ClassVar,
)

from fastapi import Depends
from typing_extensions import dataclass_transform, Protocol, Self, get_type_hints, get_origin

from .fields import FieldFilter
from .filters import create_filters
from .types import AbstractFilterOperator, FilterValues

T = TypeVar("T", covariant=True)


class FilterSpec(Protocol[T]):
    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> FieldFilter:
            pass

        @overload
        def __get__(
            self,
            instance: object,
            owner: Any,
        ) -> Optional[Mapping[AbstractFilterOperator, Union[T, List[T], bool]]]:
            pass

        def __get__(self, instance: Optional[object], owner: Any) -> Any:
            pass


class FiltersDeclMeta(type):
    def __init__(cls, name: str, bases: Any, namespace: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(name, bases, namespace, **kwargs)

        hints = get_type_hints(cls)
        specs = {key: get_args(value)[0] for key, value in hints.items() if get_origin(value) is FilterSpec}

        cls.__filter_specs__: Dict[str, FieldFilter] = {}
        for base in bases:
            cls.__filter_specs__.update(getattr(base, "__filter_specs__", {}))

        for key, value in specs.items():
            try:
                filter_field = getattr(cls, key)
            except AttributeError:
                filter_field = FieldFilter(value)
                setattr(cls, key, filter_field)

            if filter_field.type is None:
                filter_field = replace(filter_field, type=value)

            cls.__filter_specs__[key] = filter_field

        d_cls = dataclass(cls)  # type: ignore
        for key, value in cls.__filter_specs__.items():
            setattr(d_cls, key, value)


@dataclass_transform(
    field_specifiers=(FieldFilter,),
)
class FiltersDecl(metaclass=FiltersDeclMeta):
    __filter_specs__: ClassVar[Dict[str, FieldFilter]]

    def __post_init__(self) -> None:
        if any(isinstance(val, FieldFilter) for val in asdict(self).values()):  # type: ignore
            raise TypeError("Filter values incorrectly initialized")

    @classmethod
    def to_dependency(cls) -> Callable[..., Awaitable[Self]]:
        filters_dep = create_filters(**cls.__filter_specs__)  # type: ignore

        async def resolver(values: FilterValues = Depends(filters_dep)) -> Self:
            return cls(**{**dict.fromkeys(cls.__filter_specs__, None), **values})

        return resolver

    @property
    def filter_values(self) -> FilterValues:
        return {key: val for key in self.__filter_specs__ if (val := getattr(self, key)) is not None}

    def consume(self, field: str, operators: Optional[List[AbstractFilterOperator]] = None) -> Self:
        if not operators:
            setattr(self, field, None)
            return self

        for operator in operators:
            del getattr(self, field)[operator]

        if not getattr(self, field):
            setattr(self, field, None)

        return self


__all__ = [
    "FilterSpec",
    "FiltersDecl",
]
