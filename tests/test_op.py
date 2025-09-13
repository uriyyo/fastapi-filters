from typing import Optional

import pytest

from fastapi_filters import FilterField, FilterOperator, FilterSet
from fastapi_filters.op import FilterOp


class _FilterSet(FilterSet):
    a: FilterField[int] = FilterField()
    b: FilterField[Optional[str]] = FilterField()
    arr: FilterField[list[int]] = FilterField()


_field_int_a = _FilterSet.a
_field_int_b = _FilterSet.b
_field_arr = _FilterSet.arr


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        # ==, !=, <, <=, >, >=
        (_field_int_a == 1, FilterOp("a", FilterOperator.eq, 1)),
        (_field_int_a != 1, FilterOp("a", FilterOperator.ne, 1)),
        (_field_int_a < 1, FilterOp("a", FilterOperator.lt, 1)),
        (_field_int_a <= 1, FilterOp("a", FilterOperator.le, 1)),
        (_field_int_a > 1, FilterOp("a", FilterOperator.gt, 1)),
        (_field_int_a >= 1, FilterOp("a", FilterOperator.ge, 1)),
        # eq, ne, lt, le, gt, ge
        (_field_int_a.eq(1), FilterOp("a", FilterOperator.eq, 1)),
        (_field_int_a.ne(1), FilterOp("a", FilterOperator.ne, 1)),
        (_field_int_a.lt(1), FilterOp("a", FilterOperator.lt, 1)),
        (_field_int_a.le(1), FilterOp("a", FilterOperator.le, 1)),
        (_field_int_a.gt(1), FilterOp("a", FilterOperator.gt, 1)),
        (_field_int_a.ge(1), FilterOp("a", FilterOperator.ge, 1)),
        # in, not_in
        (_field_int_a.in_([1, 2]), FilterOp("a", FilterOperator.in_, [1, 2])),
        (_field_int_a >> [1, 2], FilterOp("a", FilterOperator.in_, [1, 2])),
        (_field_int_a.not_in([1, 2]), FilterOp("a", FilterOperator.not_in, [1, 2])),
        # like, not_like, ilike, not_ilike
        (_field_int_b.like("a"), FilterOp("b", FilterOperator.like, "a")),
        (_field_int_b.not_like("a"), FilterOp("b", FilterOperator.not_like, "a")),
        (_field_int_b.ilike("a"), FilterOp("b", FilterOperator.ilike, "a")),
        (_field_int_b.not_ilike("a"), FilterOp("b", FilterOperator.not_ilike, "a")),
        # is_null
        (_field_int_b.is_null(), FilterOp("b", FilterOperator.is_null, True)),
        (_field_int_b.is_null(True), FilterOp("b", FilterOperator.is_null, True)),
        (_field_int_b.is_null(False), FilterOp("b", FilterOperator.is_null, False)),
        # ov, not_ov, contains, not_contains
        (_field_arr.overlaps([1, 2]), FilterOp("arr", FilterOperator.overlap, [1, 2])),
        (
            _field_arr.not_overlaps([1, 2]),
            FilterOp("arr", FilterOperator.not_overlap, [1, 2]),
        ),
        (_field_arr.contains(1), FilterOp("arr", FilterOperator.contains, 1)),
        (_field_arr.not_contains(1), FilterOp("arr", FilterOperator.not_contains, 1)),
        # (eq, 1)
        (_field_int_a(FilterOperator.eq, 1), FilterOp("a", FilterOperator.eq, 1)),
    ],
    ids=[
        "eq-op",
        "ne-op",
        "lt-op",
        "le-op",
        "gt-op",
        "ge-op",
        "eq-func",
        "ne-func",
        "lt-func",
        "le-func",
        "gt-func",
        "ge-func",
        "in-func",
        "not-in-func",
        "in-op",
        "like-func",
        "not-like-func",
        "ilike-func",
        "not-ilike-func",
        "is-null-func",
        "is-null-func-true",
        "is-null-func-false",
        "ov-func",
        "not-ov-func",
        "contains-func",
        "not-contains-func",
        "call",
    ],
)
def test_op_constructor(expr, expected):
    assert expr == expected


def test_missed_fields():
    _field_no_name = FilterField(type=int, operators=[FilterOperator.eq])

    with pytest.raises(
        AssertionError,
        match="^FilterField has no name$",
    ):
        _ = _field_no_name == 1

    _field_no_type = FilterField(name="a")

    with pytest.raises(
        AssertionError,
        match="^FilterField has no operators$",
    ):
        _ = _field_no_type == 1
