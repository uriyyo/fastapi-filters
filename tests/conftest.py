from asyncio import new_event_loop
from inspect import iscoroutinefunction

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pytest import Function
from pytest import fixture
from pytest_asyncio import fixture as async_fixture


def pytest_collection_modifyitems(items):
    items.sort(key=lambda it: (it.path, it.name))

    for item in items:
        if isinstance(item, Function) and iscoroutinefunction(item.obj):
            item.add_marker("asyncio")


@fixture(scope="session")
def event_loop():
    return new_event_loop()


@fixture
def app():
    return FastAPI()


@async_fixture
async def client(app):
    async with LifespanManager(app), AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
