# Sorting

`fastapi-filters` provides built-in sorting support that integrates with the same database backends
as filtering.

## Basic Usage

Use `create_sorting` to define sortable fields:

```python
from fastapi import Depends, FastAPI

from fastapi_filters import SortingValues, create_sorting

app = FastAPI()


@app.get("/users")
async def get_users(
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    return {"sorting": sorting}
```

Clients specify sort order using `+` (ascending) and `-` (descending) prefixes:

```
GET /users?sort=+age,-created_at
```

---

## Default Sort

Set a default sort order that applies when no `sort` parameter is provided:

```python
sorting = create_sorting(
    "age", "created_at",
    default="+age",
)

# Multiple defaults
sorting = create_sorting(
    "age", "created_at",
    default=["+age", "-created_at"],
)
```

---

## From Pydantic Model

Auto-generate sortable fields from a Pydantic model:

```python
from pydantic import BaseModel

from fastapi_filters import create_sorting_from_model


class UserOut(BaseModel):
    name: str
    age: int
    created_at: datetime


sorting = create_sorting_from_model(
    UserOut,
    default="+age",
    exclude={"name"},  # exclude specific fields
)
```

Complex fields (nested models, lists) are automatically excluded.

---

## NULL Positioning

Control where NULL values appear in sorted results:

```python
sorting = create_sorting(
    "age",
    ("created_at", "bigger"),   # NULLs sort as "bigger" (last in ASC, first in DESC)
    ("deleted_at", "smaller"),  # NULLs sort as "smaller" (first in ASC, last in DESC)
)
```

---

## Combined with Filters

Sorting works alongside `FilterSet` in your endpoints:

```python
from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    ...
```

And applied together with database integrations:

```python
from sqlalchemy import select
from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    stmt = apply_filters_and_sorting(select(User), filters, sorting)
    ...
```

---

## Custom Query Parameter Alias

By default, the sorting parameter is named `sort`. You can change it:

```python
sorting = create_sorting(
    "age", "created_at",
    alias="order_by",
)
```

Now clients use `?order_by=+age,-created_at`.

---

## SortingValues Structure

`SortingValues` is a list of tuples: `list[tuple[str, SortingDirection, SortingNulls]]`

- `str` -- field name
- `SortingDirection` -- `"asc"` or `"desc"`
- `SortingNulls` -- `"bigger"`, `"smaller"`, or `None`

```python
# GET /users?sort=+age,-created_at
# Produces:
[
    ("age", "asc", None),
    ("created_at", "desc", None),
]
```
