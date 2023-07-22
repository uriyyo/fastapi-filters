from typing import List, TypeVar, Any

from pydantic import BeforeValidator, GetPydanticSchema
from typing_extensions import TypeAlias, Annotated

T = TypeVar("T")


def csv_list_validator(v: Any) -> Any:
    if isinstance(v, str):
        return v.split(",")
    if isinstance(v, list) and len(v) == 1 and isinstance(v[0], str):
        return v[0].split(",")

    return v


CSVList: TypeAlias = Annotated[
    List[T],
    BeforeValidator(csv_list_validator),
    GetPydanticSchema(
        get_pydantic_json_schema=lambda core_schema, handler: {
            **handler.resolve_ref_schema(handler(core_schema)),
            "explode": False,
        }
    ),
]

__all__ = [
    "CSVList",
]
