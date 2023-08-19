from typing import List

from typing_extensions import reveal_type
from fastapi_filters import FilterField

field: FilterField[List[str]] = FilterField()

reveal_type(field.ov(["1", "2", "3"]))
reveal_type(field.not_ov(["1", "2", "3"]))
reveal_type(field.contains("1"))
reveal_type(field.not_contains("1"))

reveal_type(field.is_null())
reveal_type(field.is_null(True))
reveal_type(field.is_null(False))

# output:
"""
:8:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.str]]"
:9:13: note: Revealed type is "fastapi_filters.op.FilterOp[typing.Sequence[builtins.str]]"
:10:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
:11:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.str]"
:13:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
:14:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
:15:13: note: Revealed type is "fastapi_filters.op.FilterOp[builtins.bool]"
Success: no issues found in 1 source file
"""
