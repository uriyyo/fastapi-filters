from typing import List

from typing_extensions import reveal_type, TypeAlias
from fastapi_filters import FilterField

_T: TypeAlias = List[int]
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
reveal_type(field.overlaps([val]))
reveal_type(field.not_overlaps([val]))
reveal_type(field.contains(val))
reveal_type(field.not_contains(val))

# output:
"""
tests/mypy/arr_op.py:12:13: note: Revealed type is "None"
tests/mypy/arr_op.py:13:13: note: Revealed type is "None"
tests/mypy/arr_op.py:14:13: note: Revealed type is "None"
tests/mypy/arr_op.py:15:13: note: Revealed type is "None"
tests/mypy/arr_op.py:16:13: note: Revealed type is "None"
tests/mypy/arr_op.py:17:13: note: Revealed type is "None"
tests/mypy/arr_op.py:20:13: note: Revealed type is "None"
tests/mypy/arr_op.py:21:13: note: Revealed type is "None"
tests/mypy/arr_op.py:22:13: note: Revealed type is "None"
tests/mypy/arr_op.py:23:13: note: Revealed type is "None"
tests/mypy/arr_op.py:24:13: note: Revealed type is "None"
tests/mypy/arr_op.py:25:13: note: Revealed type is "None"
tests/mypy/arr_op.py:28:13: note: Revealed type is "None"
tests/mypy/arr_op.py:29:13: note: Revealed type is "None"
tests/mypy/arr_op.py:30:13: note: Revealed type is "None"
tests/mypy/arr_op.py:33:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:34:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:35:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/arr_op.py:38:13: error: Invalid self argument "FilterField[List[int]]" to attribute function "like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op.py:38:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/arr_op.py:39:13: error: Invalid self argument "FilterField[List[int]]" to attribute function "not_like" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op.py:39:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/arr_op.py:40:13: error: Invalid self argument "FilterField[List[int]]" to attribute function "ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op.py:40:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/arr_op.py:41:13: error: Invalid self argument "FilterField[List[int]]" to attribute function "not_ilike" with type "Callable[[FilterOpBuilder[str], str], FilterOp[str]]"  [misc]
tests/mypy/arr_op.py:41:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
tests/mypy/arr_op.py:44:13: note: Revealed type is "None"
tests/mypy/arr_op.py:45:13: note: Revealed type is "None"
tests/mypy/arr_op.py:46:13: note: Revealed type is "None"
tests/mypy/arr_op.py:47:13: note: Revealed type is "None"
Found 4 errors in 1 file (checked 1 source file)
"""
