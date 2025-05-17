from __future__ import annotations

from collections.abc import AsyncIterable, Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class _ContextVarReset(Generic[T]):
    val: T
    var: ContextVar[T]
    token: Token[T]
    resetted: bool = field(default=False, init=False)

    def __enter__(self) -> _ContextVarReset[T]:
        return self

    def __exit__(self, *_: object) -> None:
        self.reset(required=False)

    def reset(self, required: bool = True) -> None:
        if required and self.resetted:
            raise ValueError("ConfigVar has already been resetted")

        if not self.resetted:
            self.var.reset(self.token)
            self.resetted = True


class ConfigVar(Generic[T]):
    def __init__(self, name: str, default: T) -> None:
        self.name = name
        self.default = default
        self.var: ContextVar[T] = ContextVar(name, default=default)

    def set(self, value: T) -> _ContextVarReset[T]:
        token = self.var.set(value)
        return _ContextVarReset(value, self.var, token)

    def get(self) -> T:
        return self.var.get()

    def dependency(self, value: T) -> Callable[[], AsyncIterable[_ContextVarReset[T]]]:
        async def _dependency() -> AsyncIterable[_ContextVarReset[T]]:
            with self.set(value) as reset:
                yield reset

        return _dependency


__all__ = [
    "ConfigVar",
]
