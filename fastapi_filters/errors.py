class FastAPIFiltersError(Exception):
    pass


class InvalidDefaultOperatorError(FastAPIFiltersError, ValueError):
    pass


__all__ = [
    "FastAPIFiltersError",
    "InvalidDefaultOperatorError",
]
