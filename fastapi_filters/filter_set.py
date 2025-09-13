import warnings

from .filterset import FilterSet, create_filters_from_set

warnings.warn(
    "fastapi_filters.filter_set is deprecated path, use fastapi_filters.filterset instead",
    DeprecationWarning,
    stacklevel=1,
)


__all__ = [
    "FilterSet",
    "create_filters_from_set",
]
