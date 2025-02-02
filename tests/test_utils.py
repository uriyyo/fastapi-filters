import sys
import threading
from collections.abc import Awaitable, Sequence
from typing import Optional, Union

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
    assert is_optional(Optional[int])
    assert is_optional(Optional[list[int]])
    assert is_optional(Optional[tuple[int, ...]])
    assert is_optional(Optional[Sequence[int]])
    assert is_optional(Union[float, int, None])

    assert not is_optional(None)
    assert not is_optional(1)
    assert not is_optional(Awaitable[int])


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Python 3.10+ required")
def test_is_optional_union_operator():
    assert is_optional(eval("int | None"))
    assert is_optional(eval("int | float | None"))

    assert not is_optional(eval("int | float"))


def test_unwrap_type():
    assert unwrap_type(Optional[int]) is int
    assert unwrap_type(Union[int, float, None]) == Union[int, float]
    assert unwrap_type(list[int]) is int
    assert unwrap_type(tuple[int, ...]) is int
    assert unwrap_type(tuple[int, float]) == Union[int, float]
    assert unwrap_type(Sequence[int]) is int
    assert unwrap_type(int) is int
    assert unwrap_type(None) is None


@pytest.mark.skipif(sys.version_info < (3, 9), reason="Python 3.9+ required")
def test_unwrap_type_generic_aliases():
    assert unwrap_type(list[int]) is int
    assert unwrap_type(tuple[int, ...]) is int
    assert unwrap_type(tuple[int, float]) == Union[int, float]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Python 3.10+ required")
def test_unwrap_type_union_operator():
    assert unwrap_type(eval("int | None")) is int
    assert unwrap_type(eval("int | float | None")) == Union[int, float]
    assert unwrap_type(eval("int | float")) == Union[int, float]


def test_unwrap_optional_type():
    assert unwrap_optional_type(Optional[int]) is int
    assert unwrap_optional_type(Optional[list[int]]) == list[int]
    assert unwrap_optional_type(Union[int, float, None]) == Union[int, float]

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
