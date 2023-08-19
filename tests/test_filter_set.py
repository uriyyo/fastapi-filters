from dataclasses import dataclass, fields
from typing import Any

from fastapi import Depends, status
from pytest import raises

from fastapi_filters import FilterSet, FilterField, FilterOperator, create_filters, create_filters_from_set


@dataclass
class _CmpFilterField:
    val: FilterField[Any]

    def __eq__(self, other: FilterField[Any]) -> bool:
        return fields(self.val) == fields(other)


def test_filter_set_decl():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str] = FilterField()
        c: FilterField[bool] = FilterField(
            default_op=FilterOperator.ne,
            operators=[FilterOperator.eq, FilterOperator.ne],
        )

    _fields = {
        "a": FilterField(int, name="a"),
        "b": FilterField(str, name="b"),
        "c": FilterField(
            bool,
            name="c",
            default_op=FilterOperator.ne,
            operators=[FilterOperator.eq, FilterOperator.ne],
        ),
    }

    assert _FilterSet.__filters__ == {k: _CmpFilterField(v) for k, v in _fields.items()}


def test_filter_set_decl_mult_inheritance():
    class _Base1(FilterSet):
        a: FilterField[int]

    class _Base2(FilterSet):
        b: FilterField[str]

    class _FilterSet(_Base1, _Base2):
        c: FilterField[bool]

    _fields = {
        "a": FilterField(int, name="a"),
        "b": FilterField(str, name="b"),
        "c": FilterField(bool, name="c"),
    }

    assert _FilterSet.__filters__ == {k: _CmpFilterField(v) for k, v in _fields.items()}


def test_filter_field_filter_values():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    _filter_set = _FilterSet(a={FilterOperator.eq: 1, FilterOperator.ne: 2}, b=None)

    assert _filter_set.filter_values == {"a": {FilterOperator.eq: 1, FilterOperator.ne: 2}}


def test_filter_field_remove_op():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    _filter_set = _FilterSet(
        a={FilterOperator.eq: 1, FilterOperator.ne: 2},
        b={FilterOperator.eq: "a", FilterOperator.ne: "b"},
    )

    _filter_set.remove_op("a", [FilterOperator.eq])

    assert _filter_set.filter_values == {
        "a": {FilterOperator.ne: 2},
        "b": {FilterOperator.eq: "a", FilterOperator.ne: "b"},
    }

    _filter_set.remove_op("a", [FilterOperator.ne])

    assert _filter_set.filter_values == {
        "b": {FilterOperator.eq: "a", FilterOperator.ne: "b"},
    }

    _filter_set.remove_op("b")

    assert _filter_set.filter_values == {}


def test_missed_field():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    _filter_set = _FilterSet(a={FilterOperator.eq: 1})

    assert _filter_set.a == {FilterOperator.eq: 1}
    assert _filter_set.b == {}


def test_from_ops():
    class _FilterSet(FilterSet):
        a: FilterField[int]

    _filter_set = _FilterSet.from_ops(
        _FilterSet.a == 1,
        _FilterSet.a != 2,
    )

    assert _filter_set == _FilterSet(a={FilterOperator.eq: 1, FilterOperator.ne: 2})


def test_from_ops_duplicates():
    class _FilterSet(FilterSet):
        a: FilterField[int]

    with raises(
        ValueError,
        match=r"^Duplicate operator eq for a$",
    ):
        _FilterSet.from_ops(
            _FilterSet.a == 1,
            _FilterSet.a == 2,
        )


def test_from_resolver():
    _filter_set = FilterSet.create_from_resolver(create_filters(a=int, b=str))

    _fields = {
        "a": FilterField(int, name="a"),
        "b": FilterField(str, name="b"),
    }

    assert issubclass(_filter_set, FilterSet)
    assert _filter_set.__filters__ == {k: _CmpFilterField(v) for k, v in _fields.items()}


async def test_create_filters_from_set(app, client):
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    @app.get("/test")
    async def route(
        _filters: _FilterSet = Depends(create_filters_from_set(_FilterSet)),
    ):
        assert isinstance(_filters, _FilterSet)
        assert _filters == _FilterSet(
            a={FilterOperator.eq: 1, FilterOperator.ne: 2},
            b={FilterOperator.eq: "a", FilterOperator.ne: "b"},
        )

        return {}

    response = await client.get(
        "/test",
        params={
            "a[eq]": "1",
            "a[ne]": "2",
            "b[eq]": "a",
            "b[ne]": "b",
        },
    )
    assert response.status_code == status.HTTP_200_OK
