# Configuration

`fastapi-filters` exposes runtime configuration through `ConfigVar` objects, all importable from
`fastapi_filters.configs`. Each `ConfigVar` is backed by a `contextvars.ContextVar`, so values
are scoped to the current async context and are safe to use in concurrent code.

## Using a ConfigVar

Every `ConfigVar` exposes the same three methods:

| Method | Description |
|--------|-------------|
| `.get()` | Return the current value |
| `.set(value)` | Set the value; returns a context manager that resets it on exit |
| `.dependency(value)` | Return a FastAPI dependency that sets the value for the request lifetime |

### As a FastAPI dependency (recommended)

```python
from fastapi import Depends, FastAPI

from fastapi_filters.configs import csv_separator_config

app = FastAPI()


@app.get("/items", dependencies=[Depends(csv_separator_config.dependency(";"))])
async def get_items():
    ...
```

### As a context manager

```python
with csv_separator_config.set(";"):
    ...  # separator is ";" inside this block
```

---

## Available Configs

### `csv_separator_config`

Controls the separator character used by `CSVList` when splitting a string into a list.

| Detail | Value |
|--------|-------|
| Import | `from fastapi_filters.configs import csv_separator_config` |
| Type | `ConfigVar[str]` |
| Default | `","` |

```python
from fastapi import Depends, FastAPI, Query

from fastapi_filters.configs import csv_separator_config
from fastapi_filters.schemas import CSVList

app = FastAPI()


@app.get("/items", dependencies=[Depends(csv_separator_config.dependency(";"))])
async def get_items(ids: CSVList[int] = Query(...)):
    return ids
# GET /items?ids=1;2;3  →  [1, 2, 3]
```

---

### `alias_generator_config`

Overrides how query parameter names (aliases) are generated for each filter field and operator.
The callable receives `(field_name, operator, explicit_alias)` and must return the final query
parameter name as a string.

| Detail | Value |
|--------|-------|
| Import | `from fastapi_filters.configs import alias_generator` |
| Type | `ConfigVar[Callable[[str, FilterOperator, str \| None], str] \| None]` |
| Default | `None` (uses the built-in `field[op]` format) |

```python
from fastapi import Depends, FastAPI

from fastapi_filters import FilterField, FilterSet
from fastapi_filters.configs import alias_generator

app = FastAPI()


def my_alias_generator(name: str, op, explicit_alias: str | None) -> str:
    base = explicit_alias or name
    return f"{base}__{op.value}"  # e.g. "name__eq" instead of "name[eq]"


@app.get("/users", dependencies=[Depends(alias_generator.dependency(my_alias_generator))])
async def get_users(filters: UserFilters = Depends()):
    ...


class UserFilters(FilterSet):
    name: FilterField[str]
```

!!! note

    `alias_generator_config` is exported from `fastapi_filters.configs` as `alias_generator`
    (without the `_config` suffix).

---

### `disabled_filters_config`

A container of operators that should be excluded from auto-generated filter sets.
Any operator present in this container will be silently skipped when building query parameters.

| Detail | Value |
|--------|-------|
| Import | `from fastapi_filters.configs import disabled_filters` |
| Type | `ConfigVar[Container[FilterOperator]]` |
| Default | `()` (no operators disabled) |

```python
from fastapi import Depends, FastAPI

from fastapi_filters import FilterField, FilterSet
from fastapi_filters.configs import disabled_filters
from fastapi_filters.operators import FilterOperator

app = FastAPI()

# Disable "like" and "ilike" globally for this endpoint
DISABLED = {FilterOperator.like, FilterOperator.ilike}


@app.get("/users", dependencies=[Depends(disabled_filters.dependency(DISABLED))])
async def get_users(filters: UserFilters = Depends()):
    ...


class UserFilters(FilterSet):
    name: FilterField[str]
```

---

### `filter_operators_generator_config`

Replaces the function that decides which operators are generated for a given Python type.
The callable receives a type and must yield `FilterOperator` values.

| Detail | Value |
|--------|-------|
| Import | `from fastapi_filters.configs import filter_operators_generator` |
| Type | `ConfigVar[Callable[[type], Iterator[FilterOperator]]]` |
| Default | `default_filter_operators_generator` |

```python
from collections.abc import Iterator

from fastapi import Depends, FastAPI

from fastapi_filters import FilterField, FilterSet
from fastapi_filters.configs import filter_operators_generator
from fastapi_filters.operators import FilterOperator

app = FastAPI()


def minimal_generator(t: type) -> Iterator[FilterOperator]:
    """Only ever expose eq and ne, regardless of type."""
    yield FilterOperator.eq
    yield FilterOperator.ne


@app.get("/users", dependencies=[Depends(filter_operators_generator.dependency(minimal_generator))])
async def get_users(filters: UserFilters = Depends()):
    ...


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
```

!!! tip

    You can combine `disabled_filters` and `filter_operators_generator` — the disabled set is
    applied **after** the generator, so `disabled_filters` is a convenient way to block a few
    specific operators without replacing the entire generator.
