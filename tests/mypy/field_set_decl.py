from typing_extensions import reveal_type

from fastapi_filters import FilterField, FilterSet


class MyFilterSet(FilterSet):
    a: FilterField[int]
    b: FilterField[float]
    c: FilterField[str]
    d: FilterField[bool]


reveal_type(MyFilterSet.a)
reveal_type(MyFilterSet.b)
reveal_type(MyFilterSet.c)
reveal_type(MyFilterSet.d)

filter_set = MyFilterSet.create()

reveal_type(filter_set.a)
reveal_type(filter_set.b)
reveal_type(filter_set.c)
reveal_type(filter_set.d)

# output:
"""
tests/mypy/field_set_decl.py:13:13: note: Revealed type is "fastapi_filters.fields.FilterField[builtins.int]"
tests/mypy/field_set_decl.py:14:13: note: Revealed type is "fastapi_filters.fields.FilterField[builtins.float]"
tests/mypy/field_set_decl.py:15:13: note: Revealed type is "fastapi_filters.fields.FilterField[builtins.str]"
tests/mypy/field_set_decl.py:16:13: note: Revealed type is "fastapi_filters.fields.FilterField[builtins.bool]"
tests/mypy/field_set_decl.py:20:13: note: Revealed type is "builtins.dict[enum.Enum, builtins.int | typing.Sequence[builtins.int] | builtins.bool]"
tests/mypy/field_set_decl.py:21:13: note: Revealed type is "builtins.dict[enum.Enum, builtins.float | typing.Sequence[builtins.float] | builtins.bool]"
tests/mypy/field_set_decl.py:22:13: note: Revealed type is "builtins.dict[enum.Enum, builtins.str | typing.Sequence[builtins.str] | builtins.bool]"
tests/mypy/field_set_decl.py:23:13: note: Revealed type is "builtins.dict[enum.Enum, builtins.bool | typing.Sequence[builtins.bool]]"
Success: no issues found in 1 source file
"""
