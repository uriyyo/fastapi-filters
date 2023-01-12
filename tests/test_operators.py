from datetime import timedelta, datetime, date
from typing import List, Tuple

from pytest import mark

from fastapi_filters.operators import get_operators, SEQ_OPERATORS, Operators, DEFAULT_OPERATORS, NUMERIC_OPERATORS


@mark.parametrize(
    "tp,operators",
    [
        *[(tp, SEQ_OPERATORS) for tp in (List[int], Tuple[float, ...])],
        (bool, [Operators.eq]),
        *[(tp, DEFAULT_OPERATORS + NUMERIC_OPERATORS) for tp in (int, float, date, datetime, timedelta)],
    ],
    ids=str,
)
def test_get_default_operators(tp, operators):
    assert {*get_operators(tp)} == {*operators}
