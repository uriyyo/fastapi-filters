# SQLAlchemy

`fastapi-filters` provides first-class SQLAlchemy integration for applying filters and sorting to
`select()` statements.

## Installation

```bash
pip install fastapi-filters[sqlalchemy]
```

---

## Basic Usage

```python
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.sqlalchemy import apply_filters, apply_sorting

app = FastAPI()


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    is_active: FilterField[bool]


@app.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    stmt = select(User)
    stmt = apply_filters(stmt, filters)
    stmt = apply_sorting(stmt, sorting)

    return (await db.scalars(stmt)).all()
```

Or use the combined helper:

```python
from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting


@app.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    stmt = apply_filters_and_sorting(select(User), filters, sorting)
    return (await db.scalars(stmt)).all()
```

---

## Additional Namespace

Use `additional` to add computed or derived columns that filters/sorting can reference:

```python
from sqlalchemy import func


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
):
    stmt = select(User)

    stmt = apply_filters_and_sorting(
        stmt,
        filters,
        sorting,
        additional={
            "name": func.lower(User.name),  # filter/sort on lowercased name
        },
    )
    ...
```

You can also use `FilterField` instances as keys:

```python
stmt = apply_filters_and_sorting(
    stmt,
    filters,
    sorting,
    additional={
        UserFilters.name: func.lower(User.name),
    },
)
```

---

## Field Remapping

Use `remapping` when the filter field name differs from the database column name:

```python
@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    stmt = apply_filters(
        select(User),
        filters,
        remapping={"name": "full_name"},  # filter "name" maps to column "full_name"
    )
    ...
```

---

## Custom Filter Logic

### Per-Call Custom Filters

Pass `apply_filter` to handle specific field/operator combinations:

```python
def my_apply_filter(stmt, ns, field, op, val):
    if field == "search" and op == FilterOperator.eq:
        return stmt.where(
            User.name.ilike(f"%{val}%") | User.email.ilike(f"%{val}%")
        )
    raise NotImplementedError  # fall back to default


stmt = apply_filters(
    select(User),
    filters,
    apply_filter=my_apply_filter,
)
```

### Per-Call Custom Condition

Pass `add_condition` to control how conditions are added to the statement:

```python
def my_add_condition(stmt, field, condition):
    if field == "tags":
        return stmt.where(condition)  # custom WHERE logic
    raise NotImplementedError  # fall back to default


stmt = apply_filters(
    select(User),
    filters,
    add_condition=my_add_condition,
)
```

## Generate Filters from ORM Model

Auto-generate filters directly from a SQLAlchemy ORM model:

```python
from fastapi import Depends
from fastapi_filters.ext.sqlalchemy import create_filters_from_orm
from fastapi_filters import FilterValues


@app.get("/users")
async def get_users(
    filters: FilterValues = Depends(create_filters_from_orm(User)),
):
    stmt = apply_filters(select(User), filters)
    ...
```

Options:

```python
create_filters_from_orm(
    User,
    include={"name", "age"},         # only these fields
    exclude={"password_hash"},       # exclude these fields
    include_fk=True,                 # include foreign key columns
    remapping={"name": "user_name"}, # rename fields
)
```

!!! tip

    Prefer using `FilterSet` over `create_filters_from_orm` for new code. `FilterSet` gives you
    type-safe field access, operator overloading, `subset()`/`extract()` methods, and inheritance.

---

## Generate Sorting from ORM Model

```python
from fastapi_filters.ext.sqlalchemy import create_sorting_from_orm


@app.get("/users")
async def get_users(
    sorting: SortingValues = Depends(create_sorting_from_orm(User, default="+age")),
):
    ...
```

---

## Full Example

```python
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI
from sqlalchemy import Integer, func, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting
from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    marks: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    is_active: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
    marks: FilterField[list[int]]
    is_active: FilterField[bool]
    created_at: FilterField[datetime]


app = FastAPI()


@app.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
) -> Any:
    stmt = apply_filters_and_sorting(
        select(User),
        filters,
        sorting,
        additional={
            "name": func.lower(User.name),
        },
    )
    return (await db.scalars(stmt)).all()
```
