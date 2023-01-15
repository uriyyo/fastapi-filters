from fastapi import Query, status
from pydantic import parse_obj_as, ValidationError
from pytest import raises

from fastapi_filters.schemas import CSVList


def test_csv_list():
    assert parse_obj_as(CSVList[int], "1") == [1]
    assert parse_obj_as(CSVList[int], "1,2") == [1, 2]
    assert parse_obj_as(CSVList[int], "1,2,3") == [1, 2, 3]


def test_csv_list_errors():
    with raises(ValidationError) as exc:
        parse_obj_as(CSVList[int], "abc")

    assert exc.value.errors() == [
        {
            "loc": ("__root__", 0),
            "msg": "value is not a valid integer",
            "type": "type_error.integer",
        }
    ]


async def test_csv_list_as_query_param(app, client):
    @app.get("/")
    def index(q: CSVList[int] = Query(...)):
        return q

    res = await client.get("/", params={"q": "1"})

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == [1]

    res = await client.get("/", params={"q": "1,abc"})

    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert res.json() == {
        "detail": [
            {
                "loc": ["query", "q", 1],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            },
        ]
    }
