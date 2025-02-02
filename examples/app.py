from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from faker import Faker
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Integer, func, select, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from fastapi_filters import (
    FilterField,
    FilterSet,
    SortingValues,
    create_filters_from_set,
    create_sorting,
)
from fastapi_filters.ext.sqlalchemy import apply_filters_and_sorting

faker = Faker()
engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    marks: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    is_active: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class UserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    age: int
    marks: list[int]
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("drop schema public cascade"))
        await conn.execute(text("create schema public"))

        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session, session.begin():
        session.add_all(
            [
                User(
                    id=uuid4(),
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    email=faker.email(),
                    marks=[
                        faker.pyint(min_value=1, max_value=5) for _ in range(faker.pyint(min_value=1, max_value=10))
                    ],
                    age=faker.pyint(min_value=1, max_value=100),
                    is_active=faker.pybool(),
                    created_at=faker.date_time_this_year(),
                )
                for _ in range(100)
            ],
        )


class UserFiltersSet(FilterSet):
    first_name: FilterField[str]
    last_name: FilterField[str]
    email: FilterField[str]
    age: FilterField[int]
    marks: FilterField[list[int]]
    is_active: FilterField[bool]
    created_at: FilterField[datetime]


@app.get("/users", response_model=list[UserOut])
async def get_users(
    filters: UserFiltersSet = Depends(create_filters_from_set(UserFiltersSet)),
    sorting: SortingValues = Depends(create_sorting("age", "created_at")),
) -> Any:
    stmt = select(User)

    stmt = apply_filters_and_sorting(
        stmt,
        filters,
        sorting,
        additional={
            "first_name": func.lower(User.first_name),
            "last_name": func.lower(User.last_name),
        },
    )

    async with AsyncSession(engine) as session:
        return await session.scalars(stmt)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
