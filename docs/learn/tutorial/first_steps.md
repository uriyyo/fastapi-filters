# First Steps

Here is a minimal example of using `fastapi-filters` to add filtering to a FastAPI endpoint:

```python
from fastapi import Depends, FastAPI

from fastapi_filters import FilterField, FilterSet

app = FastAPI()


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    return {"filters": filters.filter_values}
```

Steps:

1. Import `FilterSet` and `FilterField` from `fastapi_filters`.
2. Create a class that inherits from `FilterSet` and declare filter fields using `FilterField[<type>]` annotations.
3. Add the filter set as a parameter to your endpoint with `= Depends()` -- FastAPI resolves it via dependency injection.

When a request is made to `/users`:

- Query parameters are parsed based on the declared fields and their types.
- For example, `GET /users?name[eq]=John&age[gt]=25` filters by name equal to "John" and age greater than 25.
- If no filter parameters are provided, `filters.filter_values` returns an empty dict.

## How It Works

`FilterSet` integrates directly with FastAPI's dependency injection system. When you declare
`filters: UserFilters` as an endpoint parameter, the library:

1. Generates query parameters for each field based on its type (e.g., `str` gets `eq`, `ne`, `like`, `ilike`, etc.).
2. Parses incoming query parameters using bracket notation: `field[operator]=value`.
3. Builds a `FilterSet` instance with the parsed values, accessible via `filter_values`.

!!! tip

    `FilterSet` is the recommended way to define filters. It provides a clean, declarative syntax,
    supports operator overloading for programmatic filter construction, and works seamlessly with
    all database integrations.

## What's Next?

The following pages walk through the core building blocks:

| Page | What you'll learn |
|------|-------------------|
| [FilterSet](filter_set.md) | Full FilterSet API -- inheritance, hooks, `subset()`, `extract()`, `from_ops()` |
| [FilterField](filter_field.md) | Customizing fields -- explicit operators, aliases, internal fields, per-operator types |
| [Operators](operators.md) | All available operators and how they are auto-generated per type |
| [Programmatic Filters](programmatic_filters.md) | Building `FilterOp` objects with Python operators (`>`, `==`, `>>`) |
| [Sorting](sorting.md) | Adding sort support to your endpoints |
| [OpenAPI Docs](openapi_docs.md) | Fixing Swagger UI for CSV list parameters |
