from datetime import date, datetime, timedelta

import pytest

from fastapi_filters.operators import (
    DEFAULT_OPERATORS,
    NUM_OPERATORS,
    SEQ_OPERATORS,
    FilterOperator,
    get_filter_operators,
)


@pytest.mark.parametrize(
    ("tp", "operators"),
    [
        *[(tp, SEQ_OPERATORS) for tp in (list[int], tuple[float, ...])],
        (bool, [FilterOperator.eq, FilterOperator.ne]),
        *[(tp, DEFAULT_OPERATORS + NUM_OPERATORS) for tp in (int, float, date, datetime, timedelta)],
        (int | None, [FilterOperator.is_null, *DEFAULT_OPERATORS, *NUM_OPERATORS]),
        (list[int], SEQ_OPERATORS),
        (tuple[float, ...], SEQ_OPERATORS),
    ],
    ids=str,
)
def test_get_default_operators(tp, operators):
    assert {*get_filter_operators(tp)} == {*operators}
