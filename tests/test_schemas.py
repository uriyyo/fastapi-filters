import pytest
from dirty_equals import IsPartialDict
from fastapi import Query, status
from pydantic import ValidationError

from fastapi_filters.schemas import CSVList

from .utils import parse_obj_as


def test_csv_list():
    assert parse_obj_as(CSVList[int], "1") == [1]
    assert parse_obj_as(CSVList[int], "1,2") == [1, 2]
    assert parse_obj_as(CSVList[int], "1,2,3") == [1, 2, 3]


def test_csv_list_errors():
    with pytest.raises(ValidationError) as exc:
        parse_obj_as(CSVList[int], "abc")

    assert exc.value.errors() == [
        IsPartialDict(
            {
                "input": "abc",
                "loc": (0,),
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "type": "int_parsing",
            },
        ),
    ]


@pytest.mark.asyncio
async def test_csv_list_as_query_param(app, client):
    @app.get("/")
    def index(q: CSVList[int] = Query(...)):
        return q

    res = await client.get("/", params={"q": "1"})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == [1]

    res = await client.get("/", params={"q": "1,abc"})

    assert res.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert res.json() == {
        "detail": [
            IsPartialDict(
                {
                    "input": "1,abc",
                    "loc": ["query", "q", 0],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "type": "int_parsing",
                },
            ),
        ],
    }
