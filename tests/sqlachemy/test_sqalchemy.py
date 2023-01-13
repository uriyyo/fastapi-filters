from typing import Any

from pytest import mark
from sqlalchemy import Column, Integer, DateTime, String, select, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from fastapi_filters.ext.sqlachemy import apply_filters
from fastapi_filters.operators import Operators

Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime)

    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"))

    name = Column(String)
    age = Column(Integer)
    created_at = Column(DateTime)

    group = relationship("Group", back_populates="users")


def _compile_expr(expr: Any) -> str:
    return str(expr.compile(compile_kwargs={"literal_binds": True}))


@mark.parametrize(
    "op, val, expected",
    [
        (Operators.eq, 10, User.age == 10),
        (Operators.ne, 10, User.age != 10),
        (Operators.gt, 10, User.age > 10),
        (Operators.ge, 10, User.age >= 10),
        (Operators.lt, 10, User.age < 10),
        (Operators.le, 10, User.age <= 10),
        (Operators.in_, [10, 20], User.age.in_([10, 20])),
        (Operators.not_in, [10, 20], ~User.age.in_([10, 20])),
        (Operators.is_null, True, User.age.is_(None)),
        (Operators.is_null, False, User.age.isnot(None)),
    ],
    ids=[
        "eq",
        "ne",
        "gt",
        "ge",
        "lt",
        "le",
        "in",
        "not_in",
        "is_null",
        "is_not_null",
    ],
)
def test_apply_filters(op, val, expected):
    stmt = select(User)

    filtered_stmt = apply_filters(stmt, {"age": {op: val}})

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)


def test_apply_filters_with_join():
    stmt = select(User).join(Group)

    expected = (Group.name == "test") & (User.name != "John")

    filtered_stmt = apply_filters(
        stmt,
        {
            "group.name": {Operators.eq: "test"},
            "user.name": {Operators.ne: "John"},
        },
    )

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)
