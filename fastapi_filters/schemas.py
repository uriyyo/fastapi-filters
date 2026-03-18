from typing import Annotated, Any, TypeAlias, TypeVar

from pydantic import BeforeValidator, GetPydanticSchema

from .config import ConfigVar

csv_separator_config: ConfigVar[str] = ConfigVar("csv_separator", default=",")


def csv_list_validator(v: Any) -> Any:
    match v:
        case str():
            return v.split(csv_separator_config.get())
        case [str() as s]:
            return s.split(csv_separator_config.get())
        case _:
            return v


T = TypeVar("T")

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
    "csv_separator_config",
]
