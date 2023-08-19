from typing import List

from fastapi_filters import FilterField, FilterSet


class _FilterSet(FilterSet):
    field: FilterField[List[str]] = FilterField()


_FilterSet.from_ops(
    # cmp ops
    _FilterSet.field == ["1"],
    _FilterSet.field != ["1"],
    # cmp ops (func)
    _FilterSet.field.eq(["1"]),
    _FilterSet.field.ne(["1"]),
    # numeric ops
    _FilterSet.field < "1",
    _FilterSet.field <= "1",
    _FilterSet.field > "1",
    _FilterSet.field >= "1",
    # numeric ops (func)
    _FilterSet.field.lt("1"),
    _FilterSet.field.le("1"),
    _FilterSet.field.gt("1"),
    _FilterSet.field.ge("1"),
    # str ops
    _FilterSet.field.like("123"),
    _FilterSet.field.ilike("123"),
    _FilterSet.field.not_like("123"),
    _FilterSet.field.not_ilike("123"),
)

# output:
"""
tests/mypy/arr_op_invalid.py:12:5: error: Argument 1 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:13:5: error: Argument 2 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:15:5: error: Argument 3 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:16:5: error: Argument 4 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:18:5: error: Argument 5 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:19:5: error: Argument 6 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:20:5: error: Argument 7 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:21:5: error: Argument 8 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:23:5: error: Argument 9 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:24:5: error: Argument 10 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:25:5: error: Argument 11 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:26:5: error: Argument 12 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/arr_op_invalid.py:28:5: error: Invalid self argument "FilterField[List[str]]" to attribute function "like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op_invalid.py:29:5: error: Invalid self argument "FilterField[List[str]]" to attribute function "ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op_invalid.py:30:5: error: Invalid self argument "FilterField[List[str]]" to attribute function "not_like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op_invalid.py:31:5: error: Invalid self argument "FilterField[List[str]]" to attribute function "not_ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
Found 16 errors in 1 file (checked 1 source file)
"""
