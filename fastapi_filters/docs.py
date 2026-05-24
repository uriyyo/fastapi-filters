from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from typing import Any

from fastapi import FastAPI
from starlette.types import Lifespan


def _fix_docs(app: FastAPI) -> None:
    openapi = app.openapi()

    for endpoints in openapi["paths"].values():
        for endpoint in endpoints.values():
            for parameter in endpoint.get("parameters", ()):
                if "explode" in parameter["schema"]:
                    parameter["explode"] = parameter["schema"].pop("explode")


@asynccontextmanager
async def _lifespan_wrapper(
    _lifespan_context: Lifespan[Any],
    app: FastAPI,
) -> AsyncGenerator[Any]:
    _fix_docs(app)

    async with _lifespan_context(app) as state:
        yield state


def fix_docs(app: FastAPI) -> None:
    app.router.lifespan_context = partial(
        _lifespan_wrapper,
        app.router.lifespan_context,
    )


__all__ = [
    "fix_docs",
]
