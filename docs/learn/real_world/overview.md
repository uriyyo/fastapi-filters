# Real-World Usage Patterns

This page shows common patterns for using `fastapi-filters` in production applications.

## Pattern 1: Define a Filters Module

Create a `filters/` package in your application with reusable `FilterSet` classes:

```
app/
    filters/
        __init__.py
        common.py
        users.py
        articles.py
    api/
        endpoints/
            users.py
            articles.py
    models/
        user.py
        article.py
```

### `filters/common.py`

Define base filter sets with shared fields:

```python
from datetime import datetime

from fastapi_filters import FilterField, FilterSet


class TimestampFilters(FilterSet):
    created_at: FilterField[datetime]
    updated_at: FilterField[datetime]
```

### `filters/users.py`

Define resource-specific filter sets that inherit common fields:

```python
from fastapi_filters import FilterField, FilterSet

from .common import TimestampFilters


class UserFilters(TimestampFilters):
    name: FilterField[str]
    email: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]
```

### `filters/articles.py`

```python
from fastapi_filters import FilterField, FilterOperator, FilterSet

from .common import TimestampFilters


class ArticleFilters(TimestampFilters):
    title: FilterField[str]
    status: FilterField[str] = FilterField(
        operators=[FilterOperator.eq, FilterOperator.ne, FilterOperator.in_],
    )
    author_id: FilterField[int]
    tags: FilterField[list[str]]
```

---

## Pattern 2: Internal Fields for Multi-Tenant Apps

Use internal fields to enforce tenant isolation without exposing the filter to the API:

```python
from fastapi_filters import FilterField, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    tenant_id: FilterField[int] = FilterField(internal=True)


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    current_user: User = Depends(get_current_user),
):
    # Inject tenant filter programmatically
    tenant_filters = UserFilters.from_ops(
        UserFilters.tenant_id == current_user.tenant_id,
    )

    # Merge with user-provided filters
    stmt = apply_filters(select(User), filters)
    stmt = apply_filters(stmt, tenant_filters)

    return (await db.scalars(stmt)).all()
```

---

## Pattern 3: Extract and Apply Filters Separately

Use `extract()` to split filters across different query stages:

```python
class OrderFilters(FilterSet):
    status: FilterField[str]
    total: FilterField[float]
    customer_name: FilterField[str]
    created_at: FilterField[datetime]


@app.get("/orders")
async def get_orders(filters: OrderFilters = Depends()):
    # Extract customer filters to apply on a joined table
    customer_filters = filters.extract("customer_name")

    # Main query with remaining filters
    stmt = select(Order).join(Customer)
    stmt = apply_filters(stmt, filters)  # status, total, created_at

    # Apply customer filters with remapping
    stmt = apply_filters(
        stmt,
        customer_filters,
        remapping={"customer_name": "name"},
        additional={"name": Customer.name},
    )

    return (await db.scalars(stmt)).all()
```

---

## Pattern 4: Sorting with Filters on Every Endpoint

Create a reusable pattern for endpoints that always need both filters and sorting:

```python
from fastapi import Depends

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]
    created_at: FilterField[datetime]


user_sorting = create_sorting(
    "name", "age", "created_at",
    default=["+created_at"],
)


@app.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(user_sorting),
):
    stmt = apply_filters_and_sorting(select(User), filters, sorting)
    return (await db.scalars(stmt)).all()


@app.get("/users/active")
async def list_active_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(user_sorting),
):
    # Combine API filters with a hardcoded filter
    extra = UserFilters.from_ops(UserFilters.is_active == True)

    stmt = apply_filters_and_sorting(select(User), filters, sorting)
    stmt = apply_filters(stmt, extra)

    return (await db.scalars(stmt)).all()
```

---

## Pattern 5: Computed Columns with Additional Namespace

Use `additional` to filter and sort on computed values:

```python
from sqlalchemy import func


class UserFilters(FilterSet):
    full_name: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("full_name", "age")),
):
    stmt = apply_filters_and_sorting(
        select(User),
        filters,
        sorting,
        additional={
            "full_name": func.concat(User.first_name, " ", User.last_name),
        },
    )
    ...
```

---

## Summary

| Pattern | When to Use |
|---------|-------------|
| Filters module | Always -- organizes filter sets in one place |
| Internal fields | Multi-tenant apps, enforcing server-side constraints |
| Extract filters | Joined queries, applying filters at different stages |
| Sorting + filters | Standard list endpoints with pagination |
| Computed columns | Filtering/sorting on derived values, concatenated fields |
