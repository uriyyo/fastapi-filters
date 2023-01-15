from typing import Any

from pytest import mark, raises
from sqlalchemy import Column, Integer, DateTime, String, select, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from fastapi_filters.ext.sqlalchemy import apply_filters, create_filters_from_orm
from fastapi_filters.operators import FilterOperator

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
        (FilterOperator.eq, 10, User.age == 10),
        (FilterOperator.ne, 10, User.age != 10),
        (FilterOperator.gt, 10, User.age > 10),
        (FilterOperator.ge, 10, User.age >= 10),
        (FilterOperator.lt, 10, User.age < 10),
        (FilterOperator.le, 10, User.age <= 10),
        (FilterOperator.in_, [10, 20], User.age.in_([10, 20])),
        (FilterOperator.not_in, [10, 20], ~User.age.in_([10, 20])),
        (FilterOperator.is_null, True, User.age.is_(None)),
        (FilterOperator.is_null, False, User.age.isnot(None)),
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
        (FilterOperator.like, "%test%", User.name.like("%test%")),
        (FilterOperator.ilike, "%test%", User.name.ilike("%test%")),
        (FilterOperator.not_like, "%test%", ~User.name.like("%test%")),
        (FilterOperator.not_ilike, "%test%", ~User.name.ilike("%test%")),
    ],
)
def test_apply_filters_string(op, val, expected):
    stmt = select(User)

    filtered_stmt = apply_filters(stmt, {"name": {op: val}})

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)


@mark.parametrize(
    "op, val, expected",
    [
        (FilterOperator.ov, ["en", "ua"], User.languages.overlap(["en", "ua"])),
        (FilterOperator.not_ov, ["en", "ua"], ~User.languages.overlap(["en", "ua"])),
        (FilterOperator.contains, "en", User.languages.contains("en")),
        (FilterOperator.not_contains, "en", ~User.languages.contains("en")),
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
            "group.name": {FilterOperator.eq: "test"},
            "user.name": {FilterOperator.ne: "John"},
        },
    )

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)


def test_unknown_operator():
    stmt = select(User)

    with raises(NotImplementedError, match=r"Operator unknown is not implemented"):
        apply_filters(stmt, {"name": {"unknown": "test"}})  # type: ignore


def test_create_filters_from_orm():
    resolver = create_filters_from_orm(User, include={"age"})

    assert resolver.__defs__ == {
        "age": ("age", FilterOperator.eq),
        "age__eq": ("age", FilterOperator.eq),
        "age__ge": ("age", FilterOperator.ge),
        "age__gt": ("age", FilterOperator.gt),
        "age__in_": ("age", FilterOperator.in_),
        "age__is_null": ("age", FilterOperator.is_null),
        "age__le": ("age", FilterOperator.le),
        "age__lt": ("age", FilterOperator.lt),
        "age__ne": ("age", FilterOperator.ne),
        "age__not_in": ("age", FilterOperator.not_in),
    }

    resolver = create_filters_from_orm(User, exclude={"id", "name", "languages", "created_at"})

    assert resolver.__defs__ == {
        "age": ("age", FilterOperator.eq),
        "age__eq": ("age", FilterOperator.eq),
        "age__ge": ("age", FilterOperator.ge),
        "age__gt": ("age", FilterOperator.gt),
        "age__in_": ("age", FilterOperator.in_),
        "age__is_null": ("age", FilterOperator.is_null),
        "age__le": ("age", FilterOperator.le),
        "age__lt": ("age", FilterOperator.lt),
        "age__ne": ("age", FilterOperator.ne),
        "age__not_in": ("age", FilterOperator.not_in),
    }

    resolver = create_filters_from_orm(User, include={"languages"})

    assert resolver.__defs__ == {
        "languages": ("languages", FilterOperator.eq),
        "languages__is_null": ("languages", FilterOperator.is_null),
        "languages__ov": ("languages", FilterOperator.ov),
        "languages__not_ov": ("languages", FilterOperator.not_ov),
        "languages__contains": ("languages", FilterOperator.contains),
        "languages__not_contains": ("languages", FilterOperator.not_contains),
    }
