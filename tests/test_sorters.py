from typing import List
from pytest import raises

from fastapi import Depends, status

from fastapi_filters.sorters import create_sorting, create_sorting_from_model
from fastapi_filters.types import SortingValues


async def test_filters_as_dep(app, client):
    @app.get("/")
    async def route(sorting: SortingValues = Depends(create_sorting("name", "age", "created_at"))) -> SortingValues:
        return sorting

    res = await client.get("/")

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == []

    res = await client.get("/", params={"sort": "+name,-age"})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == [["name", "asc"], ["age", "desc"]]


def test_create_sorting():
    model = create_sorting("name", "age", "created_at")

    assert model.__defs__ == {
        "+age": ("age", "asc"),
        "-age": ("age", "desc"),
        "+name": ("name", "asc"),
        "-name": ("name", "desc"),
        "+created_at": ("created_at", "asc"),
        "-created_at": ("created_at", "desc"),
    }


def test_create_sorting_from_model():
    from pydantic import BaseModel

    class Group(BaseModel):
        name: str

    class User(BaseModel):
        name: str
        age: int
        created_at: str
        group: Group
        languages: List[str]

    model = create_sorting_from_model(User)

    assert model.__defs__ == {
        "+age": ("age", "asc"),
        "-age": ("age", "desc"),
        "+name": ("name", "asc"),
        "-name": ("name", "desc"),
        "+created_at": ("created_at", "asc"),
        "-created_at": ("created_at", "desc"),
    }


def test_create_sorting_invalid_default():
    with raises(ValueError, match=r"^Default sort field invalid is not in .*$"):
        create_sorting("name", "age", "created_at", default="invalid")
