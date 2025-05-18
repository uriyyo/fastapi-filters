from collections.abc import Container
from typing import Annotated, Literal, cast

from fastapi import Query
from pydantic import BaseModel

from .schemas import CSVList
from .types import FilterPlace, SortingNulls, SortingResolver, SortingValues
from .utils import fields_include_exclude, is_complex_field


def create_sorting_from_model(
    model: type[BaseModel],
    *,
    default: str | None = None,
    in_: FilterPlace | None = None,
    include: Container[str] | None = None,
    exclude: Container[str] | None = None,
) -> SortingResolver:
    checker = fields_include_exclude(model.model_fields, include, exclude)

    return create_sorting(
        *[name for name, field in model.model_fields.items() if checker(name) and not is_complex_field(field)],
        in_=in_,
        default=default,
    )


def create_sorting(
    *fields: str | tuple[str, SortingNulls],
    in_: FilterPlace | None = None,
    default: str | list[str] | None = None,
    alias: str | None = None,
) -> SortingResolver:
    if in_ is None:
        in_ = Query

    normalized_fields = [(f, None) if isinstance(f, str) else f for f in fields]

    defs = {f"{d}{f}": (f, v, n) for (v, d) in (("asc", "+"), ("desc", "-")) for f, n in normalized_fields}
    tp = Literal[tuple(defs)]  # type: ignore[valid-type]

    default = [default] if isinstance(default, str) else default

    if default and (diff := {*default} - {*defs}):
        raise ValueError(
            f"Default sort field {','.join(diff)} is not in {','.join(f for f, _ in normalized_fields)}",
        )

    async def _get_sorters(
        sort: Annotated[CSVList[tp], in_(alias=alias)] = default,  # type: ignore[valid-type,assignment]
    ) -> SortingValues:
        return cast(SortingValues, [defs[f] for f in sort or ()])

    _get_sorters.__tp__ = tp  # type: ignore[attr-defined]
    _get_sorters.__defs__ = defs  # type: ignore[attr-defined]

    return cast(SortingResolver, _get_sorters)


__all__ = [
    "create_sorting",
    "create_sorting_from_model",
]
