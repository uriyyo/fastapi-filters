# Programmatic Filters

`fastapi-filters` supports building filters programmatically using Python's operator overloading.
This is especially useful for tests, seeding data, and constructing filters outside of HTTP requests.

## FilterOp

A `FilterOp` represents a single filter operation:

```python
from fastapi_filters.op import FilterOp
from fastapi_filters import FilterOperator

op = FilterOp(name="age", operator=FilterOperator.gt, value=25)
```

You rarely need to create `FilterOp` objects manually -- use operator overloading on `FilterSet` fields instead.

---

## Operator Overloading

`FilterSet` fields support Python comparison operators that produce `FilterOp` objects:

```python
from fastapi_filters import FilterField, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]


# Comparison operators
UserFilters.age == 25          # FilterOp(name='age', operator=eq, value=25)
UserFilters.age != 25          # FilterOp(name='age', operator=ne, value=25)
UserFilters.age > 18           # FilterOp(name='age', operator=gt, value=18)
UserFilters.age >= 18          # FilterOp(name='age', operator=ge, value=18)
UserFilters.age < 65           # FilterOp(name='age', operator=lt, value=65)
UserFilters.age <= 65          # FilterOp(name='age', operator=le, value=65)
```

---

## Named Methods

Every operator also has a named method:

```python
# Equivalent to operators above
UserFilters.age.eq(25)
UserFilters.age.ne(25)
UserFilters.age.gt(18)
UserFilters.age.ge(18)
UserFilters.age.lt(65)
UserFilters.age.le(65)

# String operators
UserFilters.name.like("%john%")
UserFilters.name.ilike("%john%")
UserFilters.name.not_like("%admin%")
UserFilters.name.not_ilike("%admin%")

# Membership operators
UserFilters.age.in_([25, 30, 35])
UserFilters.age.not_in([0, -1])

# The >> operator is a shorthand for in_
UserFilters.age >> [25, 30, 35]

# Null check
UserFilters.name.is_null()       # is_null=True
UserFilters.name.is_null(False)  # is_null=False
```

---

## Sequence Operators

For sequence (list/array) fields:

```python
class ItemFilters(FilterSet):
    tags: FilterField[list[str]]


ItemFilters.tags.overlaps(["python", "fastapi"])
ItemFilters.tags.not_overlaps(["deprecated"])
ItemFilters.tags.contains(["required-tag"])
ItemFilters.tags.not_contains(["banned-tag"])
```

---

## Building FilterSets from Ops

Use `FilterSet.from_ops()` to construct a filter set programmatically:

```python
filters = UserFilters.from_ops(
    UserFilters.name.ilike("%john%"),
    UserFilters.age > 18,
    UserFilters.is_active == True,
)

# Use with database integration
from sqlalchemy import select
from fastapi_filters.ext.sqlalchemy import apply_filters

stmt = apply_filters(select(User), filters)
```

---

## Use in Tests

Programmatic filters make tests clean and readable:

```python
import pytest
from httpx import AsyncClient


async def test_filter_by_age(client: AsyncClient):
    filters = UserFilters.from_ops(
        UserFilters.age >= 18,
        UserFilters.age < 65,
    )

    # Apply to a query
    stmt = apply_filters(select(User), filters)
    results = await session.scalars(stmt)

    assert all(18 <= user.age < 65 for user in results)
```

!!! tip

    Using `from_ops()` in tests ensures your filter logic matches what the API would produce,
    without needing to construct raw `FilterValues` dicts manually.
