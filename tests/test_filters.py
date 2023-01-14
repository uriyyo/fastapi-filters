from typing import List, Optional

from fastapi import Depends, status
from pydantic import BaseModel

from fastapi_filters import create_filters, FieldFilter, create_filters_from_model, FilterValues, Operators


async def test_filters_as_dep(app, client):
    @app.get("/")
    async def route(
        filters: FilterValues = Depends(
            create_filters(
                a=int,
                b=bool,
                c=List[str],
            )
        )
    ) -> FilterValues:
        return filters

    res = await client.get("/", params={"a": 1, "b": "true", "c": "a,b,c"})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "a": {"eq": 1},
        "b": {"eq": True},
        "c": {"ov": ["a", "b", "c"]},
    }

    res = await client.get("/", params={"a[eq]": 1, "a[gt]": 2, "a[lt]": 3})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "a": {"eq": 1, "gt": 2, "lt": 3},
    }


async def test_filters(app):
    resolver = create_filters(
        a=FieldFilter(
            int,
            default_op=Operators.ne,
            operators=[Operators.eq, Operators.ne],
        ),
        b=float,
        c=Optional[str],
    )

    assert resolver.__defs__ == {
        "a": ("a", Operators.ne),
        "a__eq": ("a", Operators.eq),
        "a__ne": ("a", Operators.ne),
        "b": ("b", Operators.eq),
        "b__eq": ("b", Operators.eq),
        "b__ge": ("b", Operators.ge),
        "b__gt": ("b", Operators.gt),
        "b__in_": ("b", Operators.in_),
        "b__le": ("b", Operators.le),
        "b__lt": ("b", Operators.lt),
        "b__ne": ("b", Operators.ne),
        "b__not_in": ("b", Operators.not_in),
        "c": ("c", Operators.eq),
        "c__eq": ("c", Operators.eq),
        "c__in_": ("c", Operators.in_),
        "c__is_null": ("c", Operators.is_null),
        "c__ne": ("c", Operators.ne),
        "c__not_in": ("c", Operators.not_in),
        "c__like": ("c", Operators.like),
        "c__not_like": ("c", Operators.not_like),
        "c__ilike": ("c", Operators.ilike),
        "c__not_ilike": ("c", Operators.not_ilike),
    }


async def test_filters_from_model(app):
    class UserModel(BaseModel):
        id: int
        name: str
        is_active: bool

    assert create_filters_from_model(UserModel).__defs__ == {
        "id": ("id", Operators.eq),
        "id__eq": ("id", Operators.eq),
        "id__ge": ("id", Operators.ge),
        "id__gt": ("id", Operators.gt),
        "id__in_": ("id", Operators.in_),
        "id__le": ("id", Operators.le),
        "id__lt": ("id", Operators.lt),
        "id__ne": ("id", Operators.ne),
        "id__not_in": ("id", Operators.not_in),
        "is_active": ("is_active", Operators.eq),
        "is_active__eq": ("is_active", Operators.eq),
        "name": ("name", Operators.eq),
        "name__eq": ("name", Operators.eq),
        "name__in_": ("name", Operators.in_),
        "name__ne": ("name", Operators.ne),
        "name__not_in": ("name", Operators.not_in),
        "name__like": ("name", Operators.like),
        "name__not_like": ("name", Operators.not_like),
        "name__ilike": ("name", Operators.ilike),
        "name__not_ilike": ("name", Operators.not_ilike),
    }
    assert create_filters_from_model(UserModel, include={"name"}).__defs__ == {
        "name": ("name", Operators.eq),
        "name__eq": ("name", Operators.eq),
        "name__in_": ("name", Operators.in_),
        "name__ne": ("name", Operators.ne),
        "name__not_in": ("name", Operators.not_in),
        "name__like": ("name", Operators.like),
        "name__not_like": ("name", Operators.not_like),
        "name__ilike": ("name", Operators.ilike),
        "name__not_ilike": ("name", Operators.not_ilike),
    }
    assert create_filters_from_model(UserModel, exclude={"id"}).__defs__ == {
        "is_active": ("is_active", Operators.eq),
        "is_active__eq": ("is_active", Operators.eq),
        "name": ("name", Operators.eq),
        "name__eq": ("name", Operators.eq),
        "name__in_": ("name", Operators.in_),
        "name__ne": ("name", Operators.ne),
        "name__not_in": ("name", Operators.not_in),
        "name__like": ("name", Operators.like),
        "name__not_like": ("name", Operators.not_like),
        "name__ilike": ("name", Operators.ilike),
        "name__not_ilike": ("name", Operators.not_ilike),
    }
