from typing import Any

from pytest import mark, raises
from sqlalchemy import Column, Integer, DateTime, String, select, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from fastapi_filters.ext.sqlalchemy import apply_filters
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
    languages = Column(ARRAY(String))
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


@mark.parametrize(
    "op, val, expected",
    [
        (Operators.like, "%test%", User.name.like("%test%")),
        (Operators.ilike, "%test%", User.name.ilike("%test%")),
        (Operators.not_like, "%test%", ~User.name.like("%test%")),
        (Operators.not_ilike, "%test%", ~User.name.ilike("%test%")),
    ],
)
def test_apply_filters_string(op, val, expected):
    stmt = select(User)

    filtered_stmt = apply_filters(stmt, {"name": {op: val}})

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)


@mark.parametrize(
    "op, val, expected",
    [
        (Operators.ov, ["en", "ua"], User.languages.overlap(["en", "ua"])),
        (Operators.not_ov, ["en", "ua"], ~User.languages.overlap(["en", "ua"])),
        (Operators.contains, "en", User.languages.contains("en")),
        (Operators.not_contains, "en", ~User.languages.contains("en")),
    ],
    ids=[
        "ov",
        "not_ov",
        "contains",
        "not_contains",
    ],
)
def test_arrays_apply_filters(op, val, expected):
    stmt = select(User)

    filtered_stmt = apply_filters(stmt, {"languages": {op: val}})

    actual_sql = filtered_stmt.whereclause.compile()
    expected_sql = expected.compile()

    assert str(actual_sql) == str(expected_sql)
    assert actual_sql.params == expected_sql.params


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


def test_unknown_operator():
    stmt = select(User)

    with raises(NotImplementedError, match=r"Operator unknown is not implemented"):
        apply_filters(stmt, {"name": {"unknown": "test"}})  # type: ignore
