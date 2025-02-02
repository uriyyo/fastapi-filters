from contextlib import AsyncExitStack

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import fixture as async_fixture

import fastapi_filters.configs  # noqa: F401


@pytest.fixture
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
