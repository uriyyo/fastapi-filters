from typing_extensions import reveal_type
from fastapi_filters import FilterField

field: FilterField[int] = FilterField(int)

reveal_type(field == 1)
reveal_type(field != 1)
reveal_type(field > 1)
reveal_type(field >= 1)
reveal_type(field < 1)
reveal_type(field <= 1)

reveal_type(field.eq(1))
reveal_type(field.ne(1))
reveal_type(field.gt(1))
reveal_type(field.ge(1))
reveal_type(field.lt(1))
reveal_type(field.le(1))

reveal_type(field.in_([1, 2, 3]))
reveal_type(field >> [1, 2, 3])
reveal_type(field.not_in([1, 2, 3]))

reveal_type(field.is_null())
reveal_type(field.is_null(True))
reveal_type(field.is_null(False))

# output:
"""
tests/mypy/num_op.py:6:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:7:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:8:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:9:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:10:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:11:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:13:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:14:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:15:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:16:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:17:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:18:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.int]"
tests/mypy/num_op.py:20:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/num_op.py:21:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/num_op.py:22:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.int]]"
tests/mypy/num_op.py:24:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/num_op.py:25:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
tests/mypy/num_op.py:26:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
Success: no issues found in 1 source file
"""
