import threading
from typing import List, Tuple, Sequence, Awaitable

from fastapi import Depends

from fastapi_filters.utils import async_safe, is_seq


async def test_async_safe(app, client):
    def foo() -> int:
        return threading.get_ident()

    @app.get("/")
    async def route(not_safe: int = Depends(foo), safe: int = Depends(async_safe(foo))):
        return [not_safe, safe]

    res = await client.get("/")
    a, b = res.json()

    assert a != threading.get_ident()
    assert b == threading.get_ident()


def test_is_list():
    assert is_seq(List)
    assert is_seq(List[int])
    assert is_seq(Tuple[int, ...])
    assert is_seq(Sequence[int])

    assert not is_seq(None)
    assert not is_seq(1)
    assert not is_seq(Awaitable[int])
