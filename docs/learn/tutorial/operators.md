# Operators

`fastapi-filters` supports a rich set of filter operators. Operators are automatically assigned to fields
based on their Python type, but you can always customize them.

## All Available Operators

| Operator | Query Syntax | Description |
|----------|-------------|-------------|
| `eq` | `field[eq]=value` | Equal to |
| `ne` | `field[ne]=value` | Not equal to |
| `gt` | `field[gt]=value` | Greater than |
| `ge` | `field[ge]=value` | Greater than or equal |
| `lt` | `field[lt]=value` | Less than |
| `le` | `field[le]=value` | Less than or equal |
| `like` | `field[like]=value` | SQL LIKE pattern match |
| `ilike` | `field[ilike]=value` | Case-insensitive LIKE |
| `not_like` | `field[not_like]=value` | Negated LIKE |
| `not_ilike` | `field[not_ilike]=value` | Negated case-insensitive LIKE |
| `in` | `field[in]=a,b,c` | Value in list |
| `not_in` | `field[not_in]=a,b,c` | Value not in list |
| `is_null` | `field[is_null]=true` | Is NULL / Is NOT NULL |
| `overlap` | `field[overlap]=a,b,c` | Arrays overlap |
| `not_overlap` | `field[not_overlap]=a,b,c` | Arrays do not overlap |
| `contains` | `field[contains]=a,b,c` | Array contains all values |
| `not_contains` | `field[not_contains]=a,b,c` | Array does not contain all values |

---

## Auto-Generated Operators by Type

The library generates operators based on the field's Python type:

### `bool`

| Operators |
|-----------|
| `eq`, `ne` |

### `int`, `float`, `date`, `datetime`, `timedelta`

| Operators |
|-----------|
| `eq`, `ne`, `in`, `not_in`, `gt`, `ge`, `lt`, `le` |

### `str`

| Operators |
|-----------|
| `eq`, `ne`, `in`, `not_in`, `like`, `ilike`, `not_like`, `not_ilike`, `gt`, `ge`, `lt`, `le` |

### `list[T]` (Sequence types)

| Operators |
|-----------|
| `overlap`, `not_overlap`, `contains`, `not_contains` |

### `Optional[T]` (`T | None`)

All operators for type `T` plus `is_null`.

---

## Operator Groups

The operators are organized into groups internally:

```python
from fastapi_filters.operators import (
    BOOL_OPERATORS,      # eq, ne
    DEFAULT_OPERATORS,   # eq, ne, in, not_in
    NUM_OPERATORS,       # gt, ge, lt, le
    SEQ_OPERATORS,       # overlap, not_overlap, contains, not_contains
    STR_OPERATORS,       # like, ilike, not_like, not_ilike
)
```

---

## FilterOperator Enum

All operators are defined in the `FilterOperator` enum:

```python
from fastapi_filters import FilterOperator

# Use in FilterField definitions
from fastapi_filters import FilterField, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str] = FilterField(
        operators=[FilterOperator.eq, FilterOperator.ilike],
    )
```

---

## Query Parameter Format

Filters are passed as query parameters using bracket notation:

```
GET /users?name[eq]=John&age[gt]=25&email[in]=a@test.com,b@test.com
```

- `field[operator]=value` -- explicit operator
- CSV values for list operators: `field[in]=a,b,c`
- Boolean values for `is_null`: `field[is_null]=true` or `field[is_null]=false`
