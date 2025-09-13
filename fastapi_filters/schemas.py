from typing import Annotated, Any, TypeAlias, TypeVar

from pydantic import BeforeValidator, GetPydanticSchema

T = TypeVar("T")


def csv_list_validator(v: Any, delimiter: str = ",") -> Any:
    match v:
        case str():
            return v.split(delimiter)
        case [str() as s]:
            return s.split(delimiter)
        case _:
            return v


CSVList: TypeAlias = Annotated[
    list[T],
    BeforeValidator(csv_list_validator),
    GetPydanticSchema(
        get_pydantic_json_schema=lambda core_schema, handler: {
            **handler.resolve_ref_schema(handler(core_schema)),
            "explode": False,
        },
    ),
]

__all__ = [
    "CSVList",
]
