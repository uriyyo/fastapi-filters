from collections import defaultdict
from dataclasses import asdict, dataclass, make_dataclass
from dataclasses import field as dfield
from typing import Any, Iterator, List, cast, get_args, Dict, Tuple, Optional, Type, Union, Callable, Awaitable

from fastapi import Query, Depends

from .fields import CSVList
from .operators import Operators, get_operators
from .types import FilterValues
from .utils import async_safe, is_seq


@dataclass
class FieldFilter:
    type: Type[Any]
    operators: Optional[List[Operators]] = None
    default_op: Optional[Operators] = None

    def __post_init__(self) -> None:
        if self.operators is None:
            self.operators = [*get_operators(self.type)]

        if self.default_op is None:
            if is_seq(self.type):
                self.default_op = Operators.ov
            else:
                self.default_op = Operators.eq


def adapt_type(tp: Type[Any], op: Operators) -> Any:
    if is_seq(tp):
        return CSVList[tuple(get_args(tp))]  # type: ignore

    if op == Operators.is_null:
        return bool

    if op in {Operators.in_, Operators.not_in}:
        return CSVList[tp]  # type: ignore

    return tp


def default_alias_generator(name: str, op: Operators) -> str:
    return f"{name}[{op}]"


def field_filter_to_raw_fields(
    name: str,
    field: FieldFilter,
    alias_generator: Callable[[str, Operators], str],
) -> Iterator[Tuple[str, Any, Operators, Optional[str]]]:
    yield name, field.type, cast(Operators, field.default_op), None

    for op in field.operators or ():
        yield f"{name}__{op}", field.type, op, alias_generator(name, op)


def create_filters(
    *,
    in_: Callable[..., Any] = Query,
    alias_generator: Callable[[str, Operators], str] = default_alias_generator,
    **kwargs: Union[Type[Any], FieldFilter],
) -> Callable[..., Awaitable[FilterValues]]:
    fields: Dict[str, FieldFilter] = {
        name: f_def if isinstance(f_def, FieldFilter) else FieldFilter(f_def) for name, f_def in kwargs.items()
    }

    fields_defs = [
        (name, fname, tp, alias, op)
        for name, field in fields.items()
        for fname, tp, op, alias in field_filter_to_raw_fields(name, field, alias_generator)
    ]

    defs = {fname: (name, op) for name, fname, _, _, op in fields_defs}

    filter_model = make_dataclass(
        "Filters",
        [
            (fname, adapt_type(tp, op), dfield(default=in_(None, alias=alias)))
            for _, fname, tp, alias, op in fields_defs
        ],
    )

    async def _get_filters(f: Any = Depends(async_safe(filter_model))) -> FilterValues:
        values: FilterValues = defaultdict(dict)

        for key, value in asdict(f).items():
            if value is not None:
                name, op = defs[key]
                values[name][op] = value

        return {**values}

    return _get_filters


__all__ = [
    "FieldFilter",
    "create_filters",
]
