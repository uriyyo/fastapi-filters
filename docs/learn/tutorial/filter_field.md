# FilterField

`FilterField` is a descriptor that defines an individual filter field within a `FilterSet`.
It controls the type, available operators, alias, and other behavior of each field.

## Basic Declaration

The simplest form just specifies the type:

```python
from fastapi_filters import FilterField, FilterSet


class UserFilters(FilterSet):
    name: FilterField[str]
    age: FilterField[int]
```

The type parameter determines which operators are automatically generated.
See [Operators](operators.md) for the full mapping.

---

## Custom Operators

By default, operators are auto-generated based on the field type. You can override this:

```python
from fastapi_filters import FilterField, FilterOperator, FilterSet


class UserFilters(FilterSet):
    # Only allow exact match and "in" for name
    name: FilterField[str] = FilterField(
        operators=[FilterOperator.eq, FilterOperator.in_],
    )
    # All default operators for int (eq, ne, gt, ge, lt, le, in, not_in)
    age: FilterField[int]
```

---

## Default Operator

Each field has a default operator used when the client sends a value without specifying an operator.
By default:

- Scalar types use `eq`
- Sequence types use `overlap`

You can override it:

```python
class UserFilters(FilterSet):
    name: FilterField[str] = FilterField(
        default_op=FilterOperator.ilike,
    )
```

---

## Alias

Set a custom query parameter name:

```python
class UserFilters(FilterSet):
    user_name: FilterField[str] = FilterField(alias="name")
```

Now the query parameter will be `name[eq]` instead of `user_name[eq]`.

---

## Internal Fields

Mark a field as `internal` to exclude it from the generated query parameters.
Internal fields can only be set programmatically:

```python
class UserFilters(FilterSet):
    name: FilterField[str]
    tenant_id: FilterField[int] = FilterField(internal=True)


@app.get("/users")
async def get_users(filters: UserFilters = Depends()):
    # tenant_id won't appear as a query parameter
    # but you can still use it programmatically:
    filters = UserFilters.from_ops(
        UserFilters.tenant_id == current_user.tenant_id,
    )
```

---

## Per-Operator Types

Use `op_types` to override the type for specific operators:

```python
class UserFilters(FilterSet):
    age: FilterField[int] = FilterField(
        op_types={
            FilterOperator.in_: list[int],
        },
    )
```

---

## Sequence Fields

For list/array columns, use a sequence type:

```python
from datetime import datetime


class UserFilters(FilterSet):
    name: FilterField[str]
    tags: FilterField[list[str]]
    marks: FilterField[list[int]]
```

Sequence fields automatically get sequence-specific operators: `overlap`, `not_overlap`, `contains`, `not_contains`.

---

## Optional Fields

Optional types automatically gain the `is_null` operator:

```python
class UserFilters(FilterSet):
    name: FilterField[str]
    deleted_at: FilterField[datetime | None]
```

The `deleted_at` field will have all the standard `datetime` operators plus `is_null`.
Use `deleted_at[is_null]=true` or `deleted_at[is_null]=false` in query parameters.

---

## Summary

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `type` | Auto-detected | The Python type for the field |
| `operators` | `list[FilterOperator]` | Auto-generated | Allowed operators |
| `default_op` | `FilterOperator` | `eq` / `overlap` | Default operator when none specified |
| `name` | `str` | Auto-set | Field name (set by descriptor protocol) |
| `alias` | `str` | `None` | Custom query parameter name |
| `internal` | `bool` | `False` | Exclude from query parameters |
| `op_types` | `dict` | `None` | Custom types per operator |
