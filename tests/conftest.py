from inspect import iscoroutinefunction

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pytest import Function
from pytest import fixture
from pytest_asyncio import fixture as async_fixture

import fastapi_filters.configs  # noqa


def pytest_collection_modifyitems(items):
    items.sort(key=lambda it: (it.path, it.name))

    for item in items:
        if isinstance(item, Function) and iscoroutinefunction(item.obj):
            item.add_marker("asyncio")


@fixture
def app():
    return FastAPI()


@async_fixture
async def client(app):
    async with LifespanManager(app), AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
