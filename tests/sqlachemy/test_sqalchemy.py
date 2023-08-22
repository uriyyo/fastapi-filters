from typing import Any

from pytest import mark, raises
from sqlalchemy import Column, Integer, DateTime, String, select, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from fastapi_filters import FilterSet, FilterField
from fastapi_filters.ext.sqlalchemy import (
    apply_filters,
    create_filters_from_orm,
    apply_sorting,
    create_sorting_from_orm,
    apply_filters_and_sorting,
)
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
        (FilterOperator.overlap, ["en", "ua"], User.languages.overlap(["en", "ua"])),
        (FilterOperator.not_overlap, ["en", "ua"], ~User.languages.overlap(["en", "ua"])),
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


def test_apply_filters_filter_set():
    class _FilterSet(FilterSet):
        name: FilterField[str]
        age: FilterField[int]

    stmt = select(User)

    _filter_set = _FilterSet(
        name={
            FilterOperator.eq: "John",
            FilterOperator.ne: "Doe",
        },
        age={
            FilterOperator.gt: 10,
            FilterOperator.lt: 20,
        },
    )
    filtered_stmt = apply_filters(stmt, _filter_set)

    expected = (User.name == "John") & (User.name != "Doe") & (User.age > 10) & (User.age < 20)

    assert _compile_expr(filtered_stmt.whereclause) == _compile_expr(expected)


def test_unknown_operator():
    stmt = select(User)

    with raises(NotImplementedError, match=r"Operator unknown is not implemented"):
        apply_filters(stmt, {"name": {"unknown": "test"}})  # type: ignore


def test_apply_sorting():
    stmt = select(User)

    sorted_stmt = apply_sorting(stmt, [("name", "asc", None), ("age", "desc", "bigger")])

    assert _compile_expr(sorted_stmt) == _compile_expr(stmt.order_by(User.name.asc(), User.age.desc().nulls_first()))


def test_apply_sorting_invalid_direction():
    stmt = select(User)

    with raises(ValueError, match=r"^Unknown sorting direction .*$"):
        apply_sorting(stmt, [("name", "invalid", None)])  # type: ignore


def test_apply_filtering_sorting():
    stmt = select(User)

    result_stmt = apply_filters_and_sorting(
        stmt,
        {
            "name": {FilterOperator.eq: "test"},
            "age": {FilterOperator.gt: 10},
        },
        [("name", "asc", None), ("age", "desc", None)],
    )

    assert _compile_expr(result_stmt) == _compile_expr(
        stmt.where(User.name == "test").where(User.age > 10).order_by(User.name.asc(), User.age.desc())
    )


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
        "languages__overlap": ("languages", FilterOperator.overlap),
        "languages__not_overlap": ("languages", FilterOperator.not_overlap),
        "languages__contains": ("languages", FilterOperator.contains),
        "languages__not_contains": ("languages", FilterOperator.not_contains),
    }


def test_create_sorting_from_orm():
    resolver = create_sorting_from_orm(User)

    assert resolver.__defs__ == {
        "-id": ("id", "desc", None),
        "+id": ("id", "asc", None),
        "+age": ("age", "asc", None),
        "-age": ("age", "desc", None),
        "-created_at": ("created_at", "desc", None),
        "+created_at": ("created_at", "asc", None),
        "-languages": ("languages", "desc", None),
        "+languages": ("languages", "asc", None),
        "-name": ("name", "desc", None),
        "+name": ("name", "asc", None),
    }
