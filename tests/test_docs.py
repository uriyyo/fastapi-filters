import pytest
from fastapi import Query

from fastapi_filters.docs import fix_docs
from fastapi_filters.schemas import CSVList


@pytest.fixture
def app(app):
    @app.get("/")
    def route(
        q1: CSVList[int] = Query(
            None,
            annotation=CSVList[int],
        ),  # FIXME: looks like FastAPI bug
        q2: list[int] = Query(None),
    ):
        return []

    fix_docs(app)
    return app


def test_fix_docs(app, client):
    assert app.openapi()["paths"]["/"]["get"]["parameters"] == [
        {
            "in": "query",
            "name": "q1",
            "required": False,
            "schema": {"items": {"type": "integer"}, "title": "Q1", "type": "array"},
            "explode": False,
        },
        {
            "in": "query",
            "name": "q2",
            "required": False,
            "schema": {"items": {"type": "integer"}, "title": "Q2", "type": "array"},
        },
    ]
