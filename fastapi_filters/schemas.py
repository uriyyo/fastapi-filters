from typing import Annotated, Any, TypeAlias, TypeVar

from pydantic import BeforeValidator, GetPydanticSchema

T = TypeVar("T")


def csv_list_validator(v: Any) -> Any:
    match v:
        case str():
            return v.split(",")
        case [str() as s]:
            return s.split(",")
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
