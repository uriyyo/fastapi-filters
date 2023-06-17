from typing import Literal, Optional, cast, Type, Container

from fastapi import Query
from pydantic import BaseModel

from .schemas import CSVList
from .types import FilterPlace, SortingResolver, SortingValues
from .utils import fields_include_exclude


def create_sorting_from_model(
    model: Type[BaseModel],
    *,
    default: Optional[str] = None,
    in_: Optional[FilterPlace] = None,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
) -> SortingResolver:
    checker = fields_include_exclude(model.__fields__, include, exclude)

    return create_sorting(
        *[name for name, field in model.__fields__.items() if checker(name) and not field.is_complex()],
        in_=in_,
        default=default,
    )


def create_sorting(
    *fields: str,
    in_: Optional[FilterPlace] = None,
    default: Optional[str] = None,
) -> SortingResolver:
    if in_ is None:
        in_ = Query

    defs = {f"{d}{f}": (f, v) for (v, d) in (("asc", "+"), ("desc", "-")) for f in fields}
    tp = Literal[tuple(defs)]  # type: ignore

    if default and default not in defs:
        raise ValueError(f"Default sort field {default} is not in {fields}")

    async def _get_sorters(sort: CSVList[str] = in_(default)) -> SortingValues:  # type: ignore
        return cast(SortingValues, [defs[f] for f in sort or ()])

    _get_sorters.__tp__ = tp  # type: ignore
    _get_sorters.__defs__ = defs  # type: ignore

    return cast(SortingResolver, _get_sorters)


__all__ = [
    "create_sorting",
    "create_sorting_from_model",
]
