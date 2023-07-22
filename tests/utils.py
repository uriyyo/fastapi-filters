from typing import Any

from pydantic import TypeAdapter


def parse_obj_as(tp: Any, obj: Any) -> Any:
    return TypeAdapter(tp).validate_python(obj)
