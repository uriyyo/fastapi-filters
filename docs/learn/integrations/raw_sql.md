# Raw SQL

For databases without an ORM, `fastapi-filters` can generate raw SQL `WHERE` and `ORDER BY` clauses.

## Installation

```bash
pip install fastapi-filters[raw-sql]
```

---

## Basic Usage

```python
from fastapi import Depends, FastAPI

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.raw_sql import apply_filters_and_sorting

app = FastAPI()


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    result = apply_filters_and_sorting(filters, sorting)

    # result.stmt contains the SQL clause (WHERE ... ORDER BY ...)
    # result.args contains the parameter values
    query = f"SELECT * FROM users {result.stmt}"
    rows = await db.fetch_all(query, result.args)
    return rows
```

---

## Available Functions

```python
from fastapi_filters.ext.raw_sql import (
    apply_filters,             # Generate WHERE clause
    apply_sorting,             # Generate ORDER BY clause
    apply_filters_and_sorting, # Generate both
)
```

---

## SQL Dialects

Specify the SQL dialect for proper parameter formatting:

```python
# PostgreSQL (positional params: $1, $2, ...)
result = apply_filters(filters, dialect="postgresql")

# MySQL (positional params: %s, %s, ...)
result = apply_filters(filters, dialect="mysql")

# SQLite (positional params: ?, ?, ...)
result = apply_filters(filters, dialect="sqlite")
```

---

## CompiledStatement

All functions return a `CompiledStatement` with:

- `stmt` -- the SQL string (e.g., `WHERE name = $1 AND age > $2 ORDER BY age ASC`)
- `args` -- the parameter values (e.g., `["John", 25]`)

---

## Options

```python
result = apply_filters(
    filters,
    remapping={"name": "full_name"},  # remap field to column name
    types={"age": "integer"},          # explicit SQL types
    dialect="postgresql",              # SQL dialect
    arg_start=3,                       # start parameter numbering at $3
)
```
