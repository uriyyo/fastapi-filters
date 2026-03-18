from typing import Annotated, Any, TypeAlias, TypeVar

from pydantic import BeforeValidator, GetPydanticSchema

from fastapi_filters.settings import app_settings

T = TypeVar("T")


def csv_list_validator(v: Any) -> Any:
    match v:
        case str():
            return v.split(app_settings.csv_separator)
        case [str() as s]:
            return s.split(app_settings.csv_separator)
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
