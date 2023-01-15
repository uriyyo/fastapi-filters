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

To create filters you need either define them manually using `create_filters` function or automatically generate them
based on model using `create_filters_from_model` function.

```py
from typing import List

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

# import all you need from fastapi-filters
from fastapi_filters import create_filters, create_filters_from_model, FilterValues

app = FastAPI()  # create FastAPI app


class UserOut(BaseModel):  # define your model
    name: str = Field(..., example="Steve")
    surname: str = Field(..., example="Rogers")
    age: int = Field(..., example=102)


@app.get("/users")
async def get_users_manual_filters(
    # manually define filters
    filters: FilterValues = Depends(create_filters(name=str, surname=str, age=int)),
) -> List[UserOut]:
    pass


@app.get("/users")
async def get_users_auto_filters(
    # or automatically generate filters from pydantic model
    filters: FilterValues = Depends(create_filters_from_model(UserOut)),
) -> List[UserOut]:
    pass
```

Currently, `fastapi-filters` supports `SQLAlchemy` integration.

```py
from fastapi_filters.ext.sqlalchemy import apply_filters


@app.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    filters: FilterValues = Depends(create_filters_from_model(UserOut)),
) -> List[UserOut]:
    query = apply_filters(select(UserOut), filters)
    return (await db.scalars(query)).all()
```