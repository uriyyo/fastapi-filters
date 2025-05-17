from typing import TypeAlias

from typing_extensions import reveal_type

from fastapi_filters import FilterField

_T: TypeAlias = str
val: _T = "1"

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
tests/mypy/str_op.py:13:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:14:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:15:13: note: Revealed type is "None"
tests/mypy/str_op.py:16:13: note: Revealed type is "None"
tests/mypy/str_op.py:17:13: note: Revealed type is "None"
tests/mypy/str_op.py:18:13: note: Revealed type is "None"
tests/mypy/str_op.py:21:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:22:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:23:13: note: Revealed type is "None"
tests/mypy/str_op.py:24:13: note: Revealed type is "None"
tests/mypy/str_op.py:25:13: note: Revealed type is "None"
tests/mypy/str_op.py:26:13: note: Revealed type is "None"
tests/mypy/str_op.py:29:13: note: Revealed type is "None"
tests/mypy/str_op.py:30:13: note: Revealed type is "None"
tests/mypy/str_op.py:31:13: note: Revealed type is "None"
tests/mypy/str_op.py:34:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/str_op.py:35:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/str_op.py:36:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/str_op.py:39:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:40:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:41:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:42:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/str_op.py:45:13: note: Revealed type is "None"
tests/mypy/str_op.py:46:13: note: Revealed type is "None"
tests/mypy/str_op.py:47:13: note: Revealed type is "None"
tests/mypy/str_op.py:48:13: note: Revealed type is "None"
Success: no issues found in 1 source file
"""
