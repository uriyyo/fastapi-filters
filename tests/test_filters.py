from typing import List

from fastapi import Depends, status

from fastapi_filters.filters import create_filters, FieldFilter
from fastapi_filters.operators import Operators
from fastapi_filters.types import FilterValues


async def test_filters(app, client):
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


async def test_filters_def(app, client):
    @app.get("/")
    async def route(
        filters: FilterValues = Depends(
            create_filters(
                a=FieldFilter(
                    int,
                    default_op=Operators.ne,
                    operators=[Operators.eq, Operators.ne],
                ),
            )
        )
    ) -> FilterValues:
        return filters

    res = await client.get("/", params={"a": 1})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"a": {"ne": 1}}

    res = await client.get("/", params={"a": 1, "a[eq]": 2})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"a": {"ne": 1, "eq": 2}}
