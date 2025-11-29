import threading
from collections.abc import Awaitable, Sequence

import pytest
from fastapi import Depends

from fastapi_filters.utils import (
    async_safe,
    is_optional,
    is_seq,
    unwrap_optional_type,
    unwrap_seq_type,
    unwrap_type,
)


@pytest.mark.asyncio
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


def test_is_seq():
    assert is_seq(list)
    assert is_seq(list[int])
    assert is_seq(tuple[int, ...])
    assert is_seq(Sequence[int])

    assert not is_seq(None)
    assert not is_seq(1)
    assert not is_seq(Awaitable[int])


def test_is_optional():
    assert is_optional(int | None)
    assert is_optional(list[int] | None)
    assert is_optional(tuple[int, ...] | None)
    assert is_optional(Sequence[int] | None)
    assert is_optional(float | int | None)

    assert not is_optional(None)
    assert not is_optional(1)
    assert not is_optional(Awaitable[int])


def test_is_optional_union_operator():
    assert is_optional(int | None)
    assert is_optional(int | float | None)

    assert not is_optional(int | float)


def test_unwrap_type():
    assert unwrap_type(int | None) is int
    assert unwrap_type(int | float | None) == int | float
    assert unwrap_type(list[int]) is int
    assert unwrap_type(tuple[int, ...]) is int
    assert unwrap_type(tuple[int, float]) == int | float
    assert unwrap_type(Sequence[int]) is int
    assert unwrap_type(int) is int
    assert unwrap_type(None) is None


def test_unwrap_type_generic_aliases():
    assert unwrap_type(list[int]) is int
    assert unwrap_type(tuple[int, ...]) is int
    assert unwrap_type(tuple[int, float]) == int | float


def test_unwrap_type_union_operator():
    assert unwrap_type(int | None) is int
    assert unwrap_type(int | float | None) == int | float
    assert unwrap_type(int | float) == int | float


def test_unwrap_optional_type():
    assert unwrap_optional_type(int | None) is int
    assert unwrap_optional_type(list[int] | None) == list[int]
    assert unwrap_optional_type(int | float | None) == int | float

    with pytest.raises(TypeError):
        assert unwrap_optional_type(None) is None

    with pytest.raises(TypeError):
        assert unwrap_optional_type(int) is int


def test_unwrap_seq_type():
    assert unwrap_seq_type(list[int]) is int
    assert unwrap_seq_type(tuple[int, ...]) is int
    assert unwrap_seq_type(Sequence[int]) is int

    with pytest.raises(TypeError):
        assert unwrap_seq_type(None) is None

    with pytest.raises(TypeError):
        assert unwrap_seq_type(int) is int
