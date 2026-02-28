# Beanie (MongoDB)

`fastapi-filters` supports Beanie for filtering and sorting MongoDB documents.

## Installation

```bash
pip install fastapi-filters[beanie]
```

---

## Basic Usage

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from beanie import Document, init_beanie
from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.beanie import apply_filters_and_sorting


class User(Document):
    name: str
    age: int
    marks: list[int]
    is_active: bool
    created_at: datetime

    class Settings:
        name = "users"


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    marks: FilterField[list[int]]
    is_active: FilterField[bool]
    created_at: FilterField[datetime]


@asynccontextmanager
async def lifespan(_: Any) -> AsyncIterator[None]:
    client = AsyncIOMotorClient()
    await init_beanie(database=client.test, document_models=[User])
    try:
        yield
    finally:
        client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
) -> list[User]:
    stmt = User.find()
    stmt = apply_filters_and_sorting(stmt, filters, sorting)
    return await stmt.to_list()
```

---

## Available Functions

```python
from fastapi_filters.ext.beanie import (
    apply_filters,             # Apply only filters
    apply_sorting,             # Apply only sorting
    apply_filters_and_sorting, # Apply both
)
```

All functions accept an optional `remapping` parameter:

```python
stmt = apply_filters(
    User.find(),
    filters,
    remapping={"name": "full_name"},
)
```

---

## Operator Mapping

The library maps `FilterOperator` values to Beanie query operators:

| FilterOperator | Beanie Operator |
|----------------|-----------------|
| `eq` | `Eq` |
| `ne` | `NE` |
| `gt` | `GT` |
| `ge` | `GTE` |
| `lt` | `LT` |
| `le` | `LTE` |
| `in_` | `In` |
| `not_in` | `NotIn` |
| `like` / `ilike` | `RegEx` |
