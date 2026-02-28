<h1 align="center">
<img alt="logo" src="https://raw.githubusercontent.com/uriyyo/fastapi-filters/main/logo.png">
</h1>

<div align="center">
<img alt="license" src="https://img.shields.io/badge/License-MIT-lightgrey">
<img alt="test" src="https://github.com/uriyyo/fastapi-filters/workflows/Test/badge.svg">
<img alt="codecov" src="https://codecov.io/gh/uriyyo/fastapi-filters/branch/main/graph/badge.svg?token=QqIqDQ7FZi">
<a href="https://pepy.tech/project/fastapi-filters"><img alt="downloads" src="https://pepy.tech/badge/fastapi-filters"></a>
<a href="https://pypi.org/project/fastapi-filters"><img alt="pypi" src="https://img.shields.io/pypi/v/fastapi-filters"></a>
<img alt="black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</div>

## Introduction

`fastapi-filters` is a library that provides filtering/sorting feature for [FastAPI](https://fastapi.tiangolo.com/)
applications.

----

## Installation

```bash
pip install fastapi-filters
```

## Quickstart

Define filters using a `FilterSet` class:

```py
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from fastapi_filters import FilterField, FilterSet, SortingValues, create_sorting

app = FastAPI()


class UserOut(BaseModel):
    name: str
    surname: str
    age: int


class UserFilters(FilterSet):
    name: FilterField[str]
    surname: FilterField[str]
    age: FilterField[int]


@app.get("/users")
async def get_users(
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("name", "age")),
) -> list[UserOut]:
    pass
```

Query parameters are auto-generated based on field types:

```
GET /users?name[eq]=Steve&age[gt]=30&sort=+age
```

`fastapi-filters` supports `SQLAlchemy`, `Tortoise ORM`, `Beanie` (MongoDB), and raw SQL integrations.

```py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting


@app.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    filters: UserFilters = Depends(),
    sorting: SortingValues = Depends(create_sorting("name", "age")),
) -> list[UserOut]:
    stmt = apply_filters_and_sorting(select(User), filters, sorting)
    return (await db.scalars(stmt)).all()
```