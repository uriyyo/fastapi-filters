import pytest
from sqlalchemy import Integer, String

from fastapi_filters import FilterField, FilterSet
from fastapi_filters.ext.raw_sql import (
    apply_filters,
    apply_filters_and_sorting,
    apply_sorting,
    default_compile_kwargs,
    default_dialect,
)
from fastapi_filters.operators import FilterOperator


class UserFilters(FilterSet):
    age: FilterField[int]
    name: FilterField[str]


def test_apply_filters_returns_none_for_empty_filters():
    assert apply_filters({}) is None


def test_apply_filters_compiles_filter_set_with_remapping_and_types():
    filters = UserFilters(
        age={FilterOperator.gt: 18},
        name={FilterOperator.ilike: "%john%"},
    )

    compiled = apply_filters(
        filters,
        dialect="postgresql",
        remapping={"name": "user_name"},
        types={"age": Integer(), "user_name": String()},
    )

    assert compiled is not None
    assert compiled.stmt == "age > %(age_1)s AND user_name ILIKE %(user_name_1)s"
    assert compiled.args == (18, "%john%")
    assert compiled.params == {"age_1": 18, "user_name_1": "%john%"}


def test_apply_filters_uses_default_compile_options():
    with default_dialect.set("postgresql"), default_compile_kwargs.set({"literal_binds": True}):
        compiled = apply_filters(
            {"age": {FilterOperator.gt: 18}},
            types={"age": Integer()},
        )

    assert compiled is not None
    assert compiled.stmt == "age > 18"
    assert compiled.args == ()


def test_apply_filters_raises_for_unknown_operator():
    with pytest.raises(NotImplementedError, match=r"Operator unknown is not implemented"):
        apply_filters({"age": {"unknown": 18}})


def test_compiled_statement_behaves_like_two_item_tuple_for_unpacking():
    compiled = apply_filters(
        {"age": {FilterOperator.gt: 18}},
        dialect="postgresql",
    )

    assert compiled is not None
    assert len(compiled) == 2
    assert compiled[0] == "age > %(age_1)s"
    assert compiled[1] == (18,)

    with pytest.raises(IndexError, match="Index out of range for CompiledStatement"):
        compiled[2]


def test_apply_sorting_returns_none_for_empty_sorting():
    assert apply_sorting([]) is None


def test_apply_sorting_compiles_sorting_with_nulls_remapping_and_types():
    compiled = apply_sorting(
        [("age", "asc", "smaller"), ("name", "desc", None)],
        dialect="postgresql",
        remapping={"name": "user_name"},
        types={"age": Integer(), "user_name": String()},
    )

    assert compiled is not None
    assert compiled.stmt == "age ASC NULLS FIRST, user_name DESC"
    assert compiled.args == ()


def test_apply_sorting_raises_for_unknown_direction():
    with pytest.raises(ValueError, match=r"^Unknown sorting direction invalid$"):
        apply_sorting([("age", "invalid", None)])


def test_apply_filters_and_sorting_offsets_positional_sort_args():
    filters, sorting = apply_filters_and_sorting(
        {"age": {FilterOperator.gt: 18}},
        [("score", "desc", None)],
        dialect="postgresql+asyncpg",
    )

    assert filters is not None
    assert sorting is not None
    assert filters.stmt == "age > $1::INTEGER"
    assert filters.args == (18,)
    assert filters.end == 2
    assert filters.nargs == 1
    assert filters.is_positional is True
    assert sorting.stmt == "score DESC"
    assert sorting.args == ()
