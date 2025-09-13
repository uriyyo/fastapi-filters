from datetime import date, datetime, timedelta
from typing import Any, Optional

import pytest

from fastapi_filters.operators import (
    DEFAULT_OPERATORS,
    NUM_OPERATORS,
    SEQ_OPERATORS,
    FilterOperator,
    get_filter_operators,
)

ADDITIONAL_CASES: list[tuple[Any, Any]] = [
    (list[int], SEQ_OPERATORS),
    (tuple[float, ...], SEQ_OPERATORS),
    (
        int | None,
        [FilterOperator.is_null, *DEFAULT_OPERATORS, *NUM_OPERATORS],
    ),
]


@pytest.mark.parametrize(
    ("tp", "operators"),
    [
        *[(tp, SEQ_OPERATORS) for tp in (list[int], tuple[float, ...])],
        (bool, [FilterOperator.eq, FilterOperator.ne]),
        *[(tp, DEFAULT_OPERATORS + NUM_OPERATORS) for tp in (int, float, date, datetime, timedelta)],
        (Optional[int], [FilterOperator.is_null, *DEFAULT_OPERATORS, *NUM_OPERATORS]),
        *ADDITIONAL_CASES,
    ],
    ids=str,
)
def test_get_default_operators(tp, operators):
    assert {*get_filter_operators(tp)} == {*operators}
