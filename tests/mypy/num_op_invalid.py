from fastapi_filters import FilterField, FilterSet


class _FilterSet(FilterSet):
    field: FilterField[int] = FilterField(int)


_FilterSet.from_ops(
    # str ops
    _FilterSet.field.like("123"),
    _FilterSet.field.ilike("123"),
    _FilterSet.field.not_like("123"),
    _FilterSet.field.not_ilike("123"),
    # array ops
    _FilterSet.field.ov([1, 2, 3]),
    _FilterSet.field.not_ov([1, 2, 3]),
    _FilterSet.field.contains(1),
    _FilterSet.field.not_contains(1),
)

# output:
"""
tests/mypy/num_op_invalid.py:10:5: error: Invalid self argument "FilterField[int]" to attribute function "like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/num_op_invalid.py:11:5: error: Invalid self argument "FilterField[int]" to attribute function "ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/num_op_invalid.py:12:5: error: Invalid self argument "FilterField[int]" to attribute function "not_like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/num_op_invalid.py:13:5: error: Invalid self argument "FilterField[int]" to attribute function "not_ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/num_op_invalid.py:15:5: error: Argument 5 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/num_op_invalid.py:16:5: error: Argument 6 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/num_op_invalid.py:17:5: error: Argument 7 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/num_op_invalid.py:18:5: error: Argument 8 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
Found 8 errors in 1 file (checked 1 source file)
"""
