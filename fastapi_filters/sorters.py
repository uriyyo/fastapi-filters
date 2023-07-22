from typing import Literal, Optional, cast, Type, Container, Union, Tuple

from fastapi import Query
from pydantic import BaseModel

from .schemas import CSVList
from .types import FilterPlace, SortingResolver, SortingValues, SortingNulls
from .utils import fields_include_exclude, is_complex_field


def create_sorting_from_model(
    model: Type[BaseModel],
    *,
    default: Optional[str] = None,
    in_: Optional[FilterPlace] = None,
    include: Optional[Container[str]] = None,
    exclude: Optional[Container[str]] = None,
) -> SortingResolver:
    checker = fields_include_exclude(model.model_fields, include, exclude)

    return create_sorting(
        *[name for name, field in model.model_fields.items() if checker(name) and not is_complex_field(field)],
        in_=in_,
        default=default,
    )


def create_sorting(
    *fields: Union[str, Tuple[str, SortingNulls]],
    in_: Optional[FilterPlace] = None,
    default: Optional[str] = None,
) -> SortingResolver:
    if in_ is None:
        in_ = Query

    normalized_fields = [(f, None) if isinstance(f, str) else f for f in fields]

    defs = {f"{d}{f}": (f, v, n) for (v, d) in (("asc", "+"), ("desc", "-")) for f, n in normalized_fields}
    tp = Literal[tuple(defs)]  # type: ignore

    if default and default not in defs:
        raise ValueError(f"Default sort field {default} is not in {','.join(f for f, _ in normalized_fields)}")

    async def _get_sorters(sort: CSVList[tp] = in_(default, annotation=CSVList[tp])) -> SortingValues:  # type: ignore
        return cast(SortingValues, [defs[f] for f in sort or ()])

    _get_sorters.__tp__ = tp  # type: ignore
    _get_sorters.__defs__ = defs  # type: ignore

    return cast(SortingResolver, _get_sorters)


__all__ = [
    "create_sorting",
    "create_sorting_from_model",
]
