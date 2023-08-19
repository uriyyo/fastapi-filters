import sys
from datetime import timedelta, datetime, date
from typing import List, Tuple, Optional, Any

from pytest import mark

from fastapi_filters.operators import (
    get_filter_operators,
    SEQ_OPERATORS,
    FilterOperator,
    DEFAULT_OPERATORS,
    NUM_OPERATORS,
)


ADDITIONAL_CASES: List[Tuple[Any, Any]] = []

if sys.version_info >= (3, 9):
    ADDITIONAL_CASES += [
        (list[int], SEQ_OPERATORS),  # noqa
        (tuple[float, ...], SEQ_OPERATORS),  # noqa
    ]


if sys.version_info >= (3, 10):
    ADDITIONAL_CASES += [
        (eval("int | None"), [FilterOperator.is_null] + DEFAULT_OPERATORS + NUM_OPERATORS),  # noqa
    ]


@mark.parametrize(
    "tp,operators",
    [
        *[(tp, SEQ_OPERATORS) for tp in (List[int], Tuple[float, ...])],
        (bool, [FilterOperator.eq, FilterOperator.ne]),
        *[(tp, DEFAULT_OPERATORS + NUM_OPERATORS) for tp in (int, float, date, datetime, timedelta)],
        (Optional[int], [FilterOperator.is_null] + DEFAULT_OPERATORS + NUM_OPERATORS),
        *ADDITIONAL_CASES,
    ],
    ids=str,
)
def test_get_default_operators(tp, operators):
    assert {*get_filter_operators(tp)} == {*operators}
