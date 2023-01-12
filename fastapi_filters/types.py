from typing import Dict, List, Tuple, Any
from typing_extensions import TypeAlias

from .operators import Operators

FilterValues: TypeAlias = Dict[str, List[Tuple[Operators, Any]]]

__all__ = [
    "FilterValues",
]
