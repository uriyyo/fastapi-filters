from dataclasses import dataclass, fields
from typing import Any

import pytest
from fastapi import Depends, status

from fastapi_filters import (
    FilterField,
    FilterOperator,
    FilterSet,
    create_filters,
    create_filters_from_set,
)
from fastapi_filters.types import AbstractFilterOperator
from fastapi_filters.utils import unwrap_annotated

_FILTER_FIELD_ATTRS = ("type", "operators", "default_op", "name", "alias", "internal", "op_types")


@dataclass
class _CmpFilterField:  # noqa: PLW1641
    val: FilterField[Any]

    def __eq__(self, other: FilterField[Any]) -> bool:
        return all(getattr(self.val, attr) == getattr(other, attr) for attr in _FILTER_FIELD_ATTRS)


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


def test_filter_set_sequence_field():
    class _FilterSet(FilterSet):
        a: FilterField[list[int]]

    field = _FilterSet.__filters__["a"]

    assert field.type == list[int]
    assert field.default_op == FilterOperator.overlap
    assert field.operators is not None
    assert FilterOperator.overlap in field.operators


def test_filter_set_inherited_customization_preserved():
    class _Base(FilterSet):
        a: FilterField[int] = FilterField(
            default_op=FilterOperator.ne,
            operators=[FilterOperator.eq, FilterOperator.ne],
        )

    class _Child(_Base):
        b: FilterField[str]

    assert _Child.__filters__["a"].default_op == FilterOperator.ne
    assert _Child.__filters__["a"].operators == [FilterOperator.eq, FilterOperator.ne]


def test_filter_set_reused_field():
    shared = FilterField(operators=[FilterOperator.eq, FilterOperator.ne])

    class _FilterSet(FilterSet):
        a: FilterField[int] = shared
        b: FilterField[str] = shared

    assert _FilterSet.a.name == "a"
    assert _FilterSet.b.name == "b"
    assert _FilterSet.a is not _FilterSet.b
    assert _FilterSet.a is not shared

    assert shared.name is None

    assert _FilterSet.a.type is int
    assert _FilterSet.b.type is str

    assert (_FilterSet.a == 1).name == "a"
    assert (_FilterSet.b == "x").name == "b"


def test_filter_field_filter_values():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    _filter_set = _FilterSet(a={FilterOperator.eq: 1, FilterOperator.ne: 2}, b=None)

    assert _filter_set.filter_values == {
        "a": {FilterOperator.eq: 1, FilterOperator.ne: 2},
    }


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

    with pytest.raises(
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_filterset_in_decl(app, client):
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    @app.get("/test")
    async def route(
        _filters: _FilterSet = Depends(),
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


def test_subset():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]
        c: FilterField[bool]

    _filters = _FilterSet(
        a={FilterOperator.eq: 1, FilterOperator.ne: 2},
        c={FilterOperator.eq: True, FilterOperator.ne: False},
    )

    assert _filters.subset("a").filter_values == {
        "a": {FilterOperator.eq: 1, FilterOperator.ne: 2},
    }
    assert _filters.subset("b").filter_values == {}
    assert _filters.subset(_FilterSet.a, _FilterSet.b).filter_values == {
        "a": {FilterOperator.eq: 1, FilterOperator.ne: 2},
    }


def test_extract():
    class _BaseFilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]

    class _FilterSet(_BaseFilterSet):
        c: FilterField[bool]

    _filters = _FilterSet(
        a={FilterOperator.eq: 1, FilterOperator.ne: 2},
        b={FilterOperator.eq: "a", FilterOperator.ne: "b"},
        c={FilterOperator.eq: True, FilterOperator.ne: False},
    )

    extracted = _filters.extract(_FilterSet.a)

    assert extracted.filter_values == {
        "a": {FilterOperator.eq: 1, FilterOperator.ne: 2},
    }
    assert _filters.filter_values == {
        "b": {FilterOperator.eq: "a", FilterOperator.ne: "b"},
        "c": {FilterOperator.eq: True, FilterOperator.ne: False},
    }

    assert _filters.extract("d").filter_values == {}

    _filters = _FilterSet(
        a={FilterOperator.eq: 1, FilterOperator.ne: 2},
        b={FilterOperator.eq: "a", FilterOperator.ne: "b"},
        c={FilterOperator.eq: True, FilterOperator.ne: False},
    )

    assert _filters.extract(_BaseFilterSet).filter_values == {
        "a": {FilterOperator.eq: 1, FilterOperator.ne: 2},
        "b": {FilterOperator.eq: "a", FilterOperator.ne: "b"},
    }


def test_bool():
    class _FilterSet(FilterSet):
        a: FilterField[int]
        b: FilterField[str]
        c: FilterField[bool]

    assert not _FilterSet.create()
    assert _FilterSet.create(a={FilterOperator.eq: 1})
    assert _FilterSet.create(b={FilterOperator.eq: "a"})
    assert _FilterSet.create(c={FilterOperator.eq: True})


def test_op_types():
    class _FilterSet(FilterSet):
        a: FilterField[int] = FilterField(
            op_types={
                FilterOperator.eq: float,
                FilterOperator.ne: float,
            },
        )

    resolver = create_filters_from_set(_FilterSet)
    attrs = {f.name: unwrap_annotated(f.type) for f in fields(resolver.__model__)}

    assert attrs == {
        "a": float,
        "a__eq": float,
        "a__ne": float,
        "a__in_": list[int],
        "a__not_in": list[int],
        "a__gt": int,
        "a__ge": int,
        "a__lt": int,
        "a__le": int,
    }


def test_filter_set_hooks():
    class _FilterSet(FilterSet):
        a: FilterField[int]

        @classmethod
        def __filter_field_generate_alias__(
            cls,
            name: str,
            op: AbstractFilterOperator,
            alias: str | None = None,
        ) -> str:
            return f"filter-{name}-{op}"

        @classmethod
        def __filter_field_adapt_type__(
            cls,
            field: FilterField[Any],
            tp: type[Any],
            op: AbstractFilterOperator,
        ) -> Any:
            return str

    resolver = create_filters_from_set(_FilterSet)
    attrs = {f.name: unwrap_annotated(f.type) for f in fields(resolver.__model__)}

    assert attrs == {
        "a": str,
        "a__eq": str,
        "a__ne": str,
        "a__in_": str,
        "a__not_in": str,
        "a__gt": str,
        "a__ge": str,
        "a__lt": str,
        "a__le": str,
    }


@pytest.mark.asyncio
async def test_internal_filter_field_excluded_from_dependency(app, client):
    class _FilterSet(FilterSet):
        name: FilterField[str]
        tenant_id: FilterField[int] = FilterField(internal=True)

    @app.get("/test")
    async def route(
        _filters: _FilterSet = Depends(),
    ):
        assert isinstance(_filters, _FilterSet)
        return _filters.filter_values

    response = await client.get(
        "/test",
        params={
            "name[eq]": "John",
            "tenant_id[eq]": "1",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"name": {"eq": "John"}}


def test_internal_filter_field_can_be_set_programmatically():
    class _FilterSet(FilterSet):
        name: FilterField[str]
        tenant_id: FilterField[int] = FilterField(internal=True)

    filters = _FilterSet.from_ops(
        _FilterSet.name == "John",
        _FilterSet.tenant_id == 1,
    )

    assert filters.filter_values == {
        "name": {FilterOperator.eq: "John"},
        "tenant_id": {FilterOperator.eq: 1},
    }
