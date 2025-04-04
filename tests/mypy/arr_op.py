from typing_extensions import TypeAlias, reveal_type

from fastapi_filters import FilterField

_T: TypeAlias = list[int]
val: _T = [1]

field: FilterField[_T] = FilterField()

# cmp operators
reveal_type(field == val)
reveal_type(field != val)
reveal_type(field > val)
reveal_type(field >= val)
reveal_type(field < val)
reveal_type(field <= val)

# cmp operators (funcs)
reveal_type(field.eq(val))
reveal_type(field.ne(val))
reveal_type(field.gt(val))
reveal_type(field.ge(val))
reveal_type(field.lt(val))
reveal_type(field.le(val))

# in/not in
reveal_type(field.in_([val]))
reveal_type(field >> [val])
reveal_type(field.not_in([val]))

# is null operators
reveal_type(field.is_null())
reveal_type(field.is_null(True))
reveal_type(field.is_null(False))

# str operators
reveal_type(field.like("1"))
reveal_type(field.not_like("1"))
reveal_type(field.ilike("1"))
reveal_type(field.not_ilike("1"))

# array operators
reveal_type(field.overlaps(val))
reveal_type(field.not_overlaps(val))
reveal_type(field.contains(val))
reveal_type(field.not_contains(val))

# output:
"""
tests/mypy/arr_op.py:11:13: note: Revealed type is "None"
tests/mypy/arr_op.py:12:13: note: Revealed type is "None"
tests/mypy/arr_op.py:13:13: note: Revealed type is "None"
tests/mypy/arr_op.py:14:13: note: Revealed type is "None"
tests/mypy/arr_op.py:15:13: note: Revealed type is "None"
tests/mypy/arr_op.py:16:13: note: Revealed type is "None"
tests/mypy/arr_op.py:19:13: note: Revealed type is "None"
tests/mypy/arr_op.py:20:13: note: Revealed type is "None"
tests/mypy/arr_op.py:21:13: note: Revealed type is "None"
tests/mypy/arr_op.py:22:13: note: Revealed type is "None"
tests/mypy/arr_op.py:23:13: note: Revealed type is "None"
tests/mypy/arr_op.py:24:13: note: Revealed type is "None"
tests/mypy/arr_op.py:27:13: note: Revealed type is "None"
tests/mypy/arr_op.py:28:13: note: Revealed type is "None"
tests/mypy/arr_op.py:29:13: note: Revealed type is "None"
tests/mypy/arr_op.py:32:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:33:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:34:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:37:13: note: Revealed type is "None"
tests/mypy/arr_op.py:38:13: note: Revealed type is "None"
tests/mypy/arr_op.py:39:13: note: Revealed type is "None"
tests/mypy/arr_op.py:40:13: note: Revealed type is "None"
tests/mypy/arr_op.py:43:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/arr_op.py:44:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/arr_op.py:45:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/arr_op.py:46:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
Success: no issues found in 1 source file
"""
