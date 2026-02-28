# FilterSet

`FilterSet` is the core building block of `fastapi-filters`. It provides a declarative, class-based way to
define filters that integrate directly with FastAPI's dependency injection.

## Basic Usage

Define a `FilterSet` by subclassing it and annotating fields with `FilterField[<type>]`:

```python
from fastapi_filters import FilterField, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]
```

Use it in an endpoint with `Depends()`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # filters.filter_values returns only non-empty filters
    return {"filters": filters.filter_values}
```

The library auto-generates query parameters based on each field's type. For the `UserFilters` above,
the following query parameters become available:

- `name[eq]`, `name[ne]`, `name[like]`, `name[ilike]`, `name[in]`, ...
- `age[eq]`, `age[ne]`, `age[gt]`, `age[ge]`, `age[lt]`, `age[le]`, `age[in]`, ...
- `is_active[eq]`, `is_active[ne]`

---

## Accessing Filter Values

The `filter_values` property returns a dict of only the filters that were provided in the request:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # Example: GET /users?name[eq]=John&age[gt]=25
    # filters.filter_values == {
    #     "name": {FilterOperator.eq: "John"},
    #     "age": {FilterOperator.gt: 25},
    # }
    print(filters.filter_values)
```

You can also access individual fields directly:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # Each field is a dict of {operator: value}
    # Empty dict if no filter was provided for that field
    print(filters.name)   # e.g. {FilterOperator.eq: "John"}
    print(filters.age)    # e.g. {FilterOperator.gt: 25}
```

Use `bool(filters)` to check if any filters were provided:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    if not filters:
        return {"message": "No filters applied"}
    ...
```

---

## Inheritance

`FilterSet` supports inheritance. Child classes inherit all parent fields and can add new ones:

```python
class BaseFilters(FilterSet):
    created_at: FilterField[datetime]
    updated_at: FilterField[datetime]


class UserFilters(BaseFilters):
    name: FilterField[str]
    age: FilterField[int]


# UserFilters has: created_at, updated_at, name, age
```

---

## Subset and Extract

### `subset()`

Returns a new `FilterSet` containing only the specified fields:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # Get only name-related filters
    name_filters = filters.subset("name")
    # or using the field descriptor
    name_filters = filters.subset(UserFilters.name)
```

### `extract()`

Extracts the specified fields from the filter set, removing them from the original.
This is useful when you need to apply filters in different stages:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # Extract name filters (removes them from `filters`)
    name_filters = filters.extract("name")

    # `filters` no longer contains name filters
    # `name_filters` contains only name filters
```

`extract()` also accepts `FilterSet` subclasses to extract all fields from that set:

```python
class TimestampFilters(FilterSet):
    created_at: FilterField[datetime]
    updated_at: FilterField[datetime]


class UserFilters(TimestampFilters):
    name: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # Extract all timestamp fields at once
    ts_filters = filters.extract(TimestampFilters)
```

---

## Creating from FilterOps

You can construct a `FilterSet` programmatically using `from_ops()`:

```python
filters = UserFilters.from_ops(
    UserFilters.name == "John",
    UserFilters.age > 25,
)
# Equivalent to: GET /users?name[eq]=John&age[gt]=25
```

This is especially useful in tests:

```python
async def test_user_filters():
    filters = UserFilters.from_ops(
        UserFilters.is_active == True,
        UserFilters.age >= 18,
    )

    stmt = apply_filters(select(User), filters)
    ...
```

---

## Custom Hooks

You can override two class methods to customize how FilterSet generates query parameters.

### `__filter_field_adapt_type__`

Override the type used for a specific field/operator combination in query parameters:

```python
from typing import Any

from fastapi_filters import FilterField, FilterOperator, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]

    @classmethod
    def __filter_field_adapt_type__(cls, field, tp, op) -> Any | None:
        # Use a custom type for age's "in" operator
        if field.name == "age" and op == FilterOperator.in_:
            return list[int]
        return None  # use default behavior
```

### `__filter_field_generate_alias__`

Override the query parameter alias for a specific field/operator:

```python
class UserFilters(FilterSet):
    name: FilterField[str]

    @classmethod
    def __filter_field_generate_alias__(cls, name, op, alias) -> str | None:
        # Use double-underscore notation instead of brackets
        return f"{name}__{op.name}"
```

---

## `init_filter_set` Hook

Override `init_filter_set()` to run custom logic after the filter set is initialized:

```python
class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]

    def init_filter_set(self) -> None:
        # Runs after all fields are populated
        if self.name and self.age:
            print("Both name and age filters are active")
```

---

## `create_filters_from_set`

For cases where you need an explicit dependency function (e.g., when using `Depends()` directly),
use `create_filters_from_set`:

```python
from fastapi import Depends

from fastapi_filters import FilterField, FilterSet, create_filters_from_set


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(create_filters_from_set(UserFilters)),
):
    ...
```

!!! tip

    In most cases you don't need `create_filters_from_set` -- simply declaring `filters: UserFilters`
    as a parameter is enough. The explicit form is useful when you need to pass the dependency to
    `dependencies=[...]` on a router or endpoint.
