from contextlib import AsyncExitStack
from inspect import iscoroutinefunction

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
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
    async with AsyncExitStack() as astack:
        await astack.enter_async_context(LifespanManager(app))
        c = await astack.enter_async_context(
            AsyncClient(
                transport=ASGITransport(app),
                base_url="http://testserver",
            ),
        )

        yield c
