from fastapi_filters import FilterField, FilterSet


class _FilterSet(FilterSet):
    field: FilterField[str] = FilterField()


_FilterSet.from_ops(
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
    # array ops
    _FilterSet.field.ov(["1", "2", "3"]),
    _FilterSet.field.not_ov(["1", "2", "3"]),
    _FilterSet.field.contains("1"),
    _FilterSet.field.not_contains("1"),
)

# output:
"""
tests/mypy/str_op_invalid.py:10:5: error: Argument 1 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:11:5: error: Argument 2 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:12:5: error: Argument 3 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:13:5: error: Argument 4 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:15:5: error: Argument 5 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:16:5: error: Argument 6 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:17:5: error: Argument 7 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:18:5: error: Argument 8 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:20:5: error: Argument 9 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:21:5: error: Argument 10 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:22:5: error: Argument 11 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
tests/mypy/str_op_invalid.py:23:5: error: Argument 12 to "from_ops" of "FilterSet" has incompatible type "None"; expected "FilterOp[Any]"  [arg-type]
Found 12 errors in 1 file (checked 1 source file)
"""
