from typing import Dict, Any
from typing_extensions import TypeAlias

from .operators import Operators

FilterValues: TypeAlias = Dict[str, Dict[Operators, Any]]

__all__ = [
    "FilterValues",
]
