from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from beanie import Document, init_beanie
from faker import Faker
from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_filters import (
    FilterField,
    FilterSet,
    SortingValues,
    create_filters_from_set,
    create_sorting,
)
from fastapi_filters.ext.beanie import apply_filters_and_sorting

faker = Faker()


class User(Document):
    first_name: str
    last_name: str
    email: str
    age: int
    marks: list[int]
    is_active: bool
    created_at: datetime

    class Settings:
        name = "users"


@asynccontextmanager
async def lifespan(_: Any) -> AsyncIterator[None]:
    client = AsyncIOMotorClient()
    await init_beanie(database=client.test, document_models=[User])

    await User.delete_all()

    users = [
        User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            marks=[faker.pyint(min_value=1, max_value=5) for _ in range(faker.pyint(min_value=1, max_value=10))],
            age=faker.pyint(min_value=1, max_value=100),
            is_active=faker.pybool(),
            created_at=faker.date_time_this_year(),
        )
        for _ in range(100)
    ]

    for user in users:
        await user.insert()

    try:
        yield
    finally:
        client.close()


app = FastAPI(lifespan=lifespan)


class UserFiltersSet(FilterSet):
    first_name: FilterField[str]
    last_name: FilterField[str]
    email: FilterField[str]
    age: FilterField[int]
    marks: FilterField[list[int]]
    is_active: FilterField[bool]
    created_at: FilterField[datetime]


@app.get("/users")
async def get_users(
    filters: UserFiltersSet = Depends(create_filters_from_set(UserFiltersSet)),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
) -> list[User]:
    stmt = User.find()

    stmt = apply_filters_and_sorting(
        stmt,
        filters,
        sorting,
    )

    return await stmt.to_list()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
