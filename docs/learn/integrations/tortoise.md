# Tortoise ORM

`fastapi-filters` supports Tortoise ORM for applying filters and sorting to querysets.

## Installation

```bash
pip install fastapi-filters[tortoise-orm]
```

---

## Basic Usage

```python
from fastapi import FastAPI

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.tortoise import apply_filters_and_sorting

app = FastAPI()


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    stmt = User.all()
    stmt = apply_filters_and_sorting(stmt, filters, sorting)
    return await stmt
```

---

## Available Functions

```python
from fastapi_filters.ext.tortoise import (
    apply_filters,             # Apply only filters
    apply_sorting,             # Apply only sorting
    apply_filters_and_sorting, # Apply both
)
```

All functions accept an optional `remapping` parameter:

```python
stmt = apply_filters(
    User.all(),
    filters,
    remapping={"name": "full_name"},
)
```

---

## Operator Mapping

Tortoise ORM uses Django-style suffixes. The library maps `FilterOperator` values automatically:

| FilterOperator | Tortoise Suffix |
|----------------|-----------------|
| `eq` | (exact match) |
| `ne` | `__not` |
| `gt` | `__gt` |
| `ge` | `__gte` |
| `lt` | `__lt` |
| `le` | `__lte` |
| `like` | `__contains` |
| `ilike` | `__icontains` |
| `in_` | `__in` |
| `not_in` | `__not_in` |
| `is_null` | `__isnull` |
