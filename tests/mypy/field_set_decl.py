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
tests/mypy/field_set_decl.py:13:13: note: Revealed type is "fastapi_filters.fields.FilterField[int]"
tests/mypy/field_set_decl.py:14:13: note: Revealed type is "fastapi_filters.fields.FilterField[float]"
tests/mypy/field_set_decl.py:15:13: note: Revealed type is "fastapi_filters.fields.FilterField[str]"
tests/mypy/field_set_decl.py:16:13: note: Revealed type is "fastapi_filters.fields.FilterField[bool]"
tests/mypy/field_set_decl.py:20:13: note: Revealed type is "dict[enum.Enum, int | typing.Sequence[int] | bool]"
tests/mypy/field_set_decl.py:21:13: note: Revealed type is "dict[enum.Enum, float | typing.Sequence[float] | bool]"
tests/mypy/field_set_decl.py:22:13: note: Revealed type is "dict[enum.Enum, str | typing.Sequence[str] | bool]"
tests/mypy/field_set_decl.py:23:13: note: Revealed type is "dict[enum.Enum, bool | typing.Sequence[bool]]"
Success: no issues found in 1 source file
"""
