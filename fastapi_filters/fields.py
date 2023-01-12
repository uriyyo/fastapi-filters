from typing import TYPE_CHECKING, List, TypeVar, Any, Dict, ClassVar, Tuple, Iterator

from pydantic import create_model, ValidationError
from pydantic.validators import str_validator
from typing_extensions import TypeAlias

T = TypeVar("T")

if TYPE_CHECKING:
    CSVList: TypeAlias = List[T]
else:

    class CSVList(List[T]):
        __separator__: ClassVar[str] = ","

        __args__: ClassVar[Tuple[Any, ...]]

        def __class_getitem__(cls, item: Any) -> Any:
            alias = super().__class_getitem__(item)

            class _CSVList(alias):
                __origin__ = alias.__origin__
                __args__ = alias.__args__

            return _CSVList

        @classmethod
        def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
            field_schema.update(explode=False)

        @classmethod
        def __get_validators__(cls):
            def _unwrap(val: Any) -> Any:
                if isinstance(val, list) and len(val) == 1:
                    return val[0]

                return val

            yield _unwrap
            yield str_validator
            yield lambda v: v.split(cls.__separator__)

            inner_model = create_model(
                "CSVList",
                __root__=(List[cls.__args__], ...),
            )

            def _inner_parser(val: Any) -> Any:
                try:
                    return inner_model.parse_obj(val).__root__
                except ValidationError as e:
                    for err in _flatten(e.raw_errors):
                        err._loc = err._loc[1:]

                    raise e

            yield _inner_parser

    def _flatten(obj: Any) -> Iterator[Any]:
        if isinstance(obj, list):
            for item in obj:
                yield from _flatten(item)
        else:
            yield obj


__all__ = [
    "CSVList",
]
