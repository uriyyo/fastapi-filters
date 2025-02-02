from typing import Annotated, Optional

import pytest
from fastapi import Depends, status
from pydantic import BaseModel, BeforeValidator

from fastapi_filters import (
    FilterField,
    FilterOperator,
    FilterValues,
    create_filters,
    create_filters_from_model,
)


@pytest.mark.asyncio
async def test_filters_as_dep(app, client):
    @app.get("/")
    async def route(
        filters: FilterValues = Depends(
            create_filters(
                a=int,
                b=bool,
                c=list[str],
                d=FilterField(
                    bytes,
                    default_op=FilterOperator.eq,
                    operators=[FilterOperator.eq, FilterOperator.ne],
                    alias="d_alias",
                ),
            ),
        ),
    ) -> FilterValues:
        return filters

    res = await client.get(
        "/",
        params={"a": 1, "b": "true", "c": "a,b,c", "d_alias": "123"},
    )

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "a": {"eq": 1},
        "b": {"eq": True},
        "c": {"overlap": ["a", "b", "c"]},
        "d": {"eq": "123"},
    }

    res = await client.get("/", params={"a[eq]": 1, "a[gt]": 2, "a[lt]": 3})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "a": {"eq": 1, "gt": 2, "lt": 3},
    }


@pytest.mark.asyncio
async def test_filters(app):
    resolver = create_filters(
        a=FilterField(
            int,
            default_op=FilterOperator.ne,
            operators=[FilterOperator.eq, FilterOperator.ne],
        ),
        b=float,
        c=Optional[str],
    )

    assert resolver.__defs__ == {
        "a": ("a", FilterOperator.ne),
        "a__eq": ("a", FilterOperator.eq),
        "a__ne": ("a", FilterOperator.ne),
        "b": ("b", FilterOperator.eq),
        "b__eq": ("b", FilterOperator.eq),
        "b__ge": ("b", FilterOperator.ge),
        "b__gt": ("b", FilterOperator.gt),
        "b__in_": ("b", FilterOperator.in_),
        "b__le": ("b", FilterOperator.le),
        "b__lt": ("b", FilterOperator.lt),
        "b__ne": ("b", FilterOperator.ne),
        "b__not_in": ("b", FilterOperator.not_in),
        "c": ("c", FilterOperator.eq),
        "c__eq": ("c", FilterOperator.eq),
        "c__in_": ("c", FilterOperator.in_),
        "c__is_null": ("c", FilterOperator.is_null),
        "c__ne": ("c", FilterOperator.ne),
        "c__not_in": ("c", FilterOperator.not_in),
        "c__like": ("c", FilterOperator.like),
        "c__not_like": ("c", FilterOperator.not_like),
        "c__ilike": ("c", FilterOperator.ilike),
        "c__not_ilike": ("c", FilterOperator.not_ilike),
    }


@pytest.mark.asyncio
async def test_filters_from_model(app):
    class UserModel(BaseModel):
        id: int
        name: Annotated[str, BeforeValidator(lambda v: v)]
        is_active: bool

    assert create_filters_from_model(UserModel).__defs__ == {
        "id": ("id", FilterOperator.eq),
        "id__eq": ("id", FilterOperator.eq),
        "id__ge": ("id", FilterOperator.ge),
        "id__gt": ("id", FilterOperator.gt),
        "id__in_": ("id", FilterOperator.in_),
        "id__le": ("id", FilterOperator.le),
        "id__lt": ("id", FilterOperator.lt),
        "id__ne": ("id", FilterOperator.ne),
        "id__not_in": ("id", FilterOperator.not_in),
        "is_active": ("is_active", FilterOperator.eq),
        "is_active__eq": ("is_active", FilterOperator.eq),
        "is_active__ne": ("is_active", FilterOperator.ne),
        "name": ("name", FilterOperator.eq),
        "name__eq": ("name", FilterOperator.eq),
        "name__in_": ("name", FilterOperator.in_),
        "name__ne": ("name", FilterOperator.ne),
        "name__not_in": ("name", FilterOperator.not_in),
        "name__like": ("name", FilterOperator.like),
        "name__not_like": ("name", FilterOperator.not_like),
        "name__ilike": ("name", FilterOperator.ilike),
        "name__not_ilike": ("name", FilterOperator.not_ilike),
    }
    assert create_filters_from_model(UserModel, include={"name"}).__defs__ == {
        "name": ("name", FilterOperator.eq),
        "name__eq": ("name", FilterOperator.eq),
        "name__in_": ("name", FilterOperator.in_),
        "name__ne": ("name", FilterOperator.ne),
        "name__not_in": ("name", FilterOperator.not_in),
        "name__like": ("name", FilterOperator.like),
        "name__not_like": ("name", FilterOperator.not_like),
        "name__ilike": ("name", FilterOperator.ilike),
        "name__not_ilike": ("name", FilterOperator.not_ilike),
    }
    assert create_filters_from_model(UserModel, exclude={"id"}).__defs__ == {
        "is_active": ("is_active", FilterOperator.eq),
        "is_active__eq": ("is_active", FilterOperator.eq),
        "is_active__ne": ("is_active", FilterOperator.ne),
        "name": ("name", FilterOperator.eq),
        "name__eq": ("name", FilterOperator.eq),
        "name__in_": ("name", FilterOperator.in_),
        "name__ne": ("name", FilterOperator.ne),
        "name__not_in": ("name", FilterOperator.not_in),
        "name__like": ("name", FilterOperator.like),
        "name__not_like": ("name", FilterOperator.not_like),
        "name__ilike": ("name", FilterOperator.ilike),
        "name__not_ilike": ("name", FilterOperator.not_ilike),
    }
