from __future__ import annotations

import inspect
from collections import defaultdict
from collections.abc import Awaitable, Callable, Iterable
from typing import TYPE_CHECKING, Annotated, Any, TypeAlias, TypeVar, cast, no_type_check

from fastapi import Query

from .fields import FilterField
from .types import AbstractFilterOperator, FilterPlace

if TYPE_CHECKING:
    from .filterset import FilterSet

    _TFilterSet = TypeVar("_TFilterSet", bound=FilterSet)


_FieldToOpMapping: TypeAlias = dict[str, tuple[AbstractFilterOperator, FilterField[Any], bool]]


def _generate_param(
    filterset: type[_TFilterSet],
    field: FilterField[Any],
    op: AbstractFilterOperator,
    name: str | None = None,
    in_: FilterPlace | None = None,
    is_default: bool = False,
) -> inspect.Parameter:
    if in_ is None:
        in_ = Query

    _alias = field.alias or name if is_default else None

    return inspect.Parameter(
        name=name or f"{field.name}__{op.name}",
        kind=inspect.Parameter.KEYWORD_ONLY,
        default=None,  # TODO: use better sentinel value here
        annotation=Annotated[
            filterset.adapt_filter_field_type(
                field=field,
                tp=field.type or Any,  # type: ignore[arg-type]
                op=op,
            ),
            in_(
                alias=_alias or filterset.generate_filter_field_alias(field, op),
            ),
        ],
    )


def _generate_params(
    mapping: _FieldToOpMapping,
    filterset: type[_TFilterSet],
    in_: FilterPlace | None = None,
) -> Iterable[inspect.Parameter]:
    for name, (op, field, is_default) in mapping.items():
        yield _generate_param(
            filterset=filterset,
            field=field,
            op=op,
            name=name,
            in_=in_,
            is_default=is_default,
        )


def _op_to_field_mapping(
    filterset: type[_TFilterSet],
) -> Iterable[
    tuple[
        str,
        tuple[AbstractFilterOperator, FilterField[Any], bool],
    ],
]:
    for field in filterset.__filters__.values():
        if field.internal:
            continue

        name = cast(str, field.name)

        if field.default_op is not None:
            yield name, (field.default_op, field, True)

        for op in field.operators or ():
            yield f"{name}__{op.name}", (op, field, False)


@no_type_check
def _add_resolver_metadata(
    resolver: Callable[..., Awaitable[Any]],
    filterset: type[_TFilterSet],
    signature: inspect.Signature,
    field_to_op: _FieldToOpMapping,
) -> None:
    resolver.__signature__ = signature
    resolver.__name__ = f"{filterset.__name__}Resolver"
    resolver.__qualname__ = resolver.__name__
    resolver.__doc__ = f"Auto-generated resolver for {filterset.__name__}"

    resolver.__model__ = filterset
    resolver.__filters__ = {**filterset.__filters__}
    resolver.__defs__ = {name: (field.name, op) for name, (op, field, _) in field_to_op.items()}


def create_filterset_resolver(
    filterset: type[_TFilterSet],
    /,
    in_: FilterPlace | None = None,
    as_mapping: bool = False,
) -> Callable[..., Awaitable[Any]]:
    _field_to_op: _FieldToOpMapping = dict(_op_to_field_mapping(filterset))

    async def _filterset_resolver(**kwargs: Any) -> Any:
        field_to_op: dict[str, Any] = defaultdict(dict)

        for key, value in kwargs.items():
            if value is None:
                continue

            op, field, _ = _field_to_op[key]
            field_to_op[field.name][op] = value  # type: ignore[index]

        if as_mapping:
            return field_to_op

        return filterset.create(**field_to_op)

    signature = inspect.Signature(
        parameters=[*_generate_params(_field_to_op, filterset, in_)],
        return_annotation=filterset,
    )

    _add_resolver_metadata(
        resolver=_filterset_resolver,
        filterset=filterset,
        signature=signature,
        field_to_op=_field_to_op,
    )

    return _filterset_resolver


__all__ = [
    "create_filterset_resolver",
]
