# CSVList

`CSVList` is a type alias that parses a single comma-separated string (or a list with one string element)
into a typed list. It is the type used internally for `in`, `not_in`, and other multi-value operators.

## Basic Usage

Use `CSVList[T]` as a query parameter type directly:

```python
from fastapi import FastAPI, Query

from fastapi_filters.schemas import CSVList

app = FastAPI()


@app.get("/items")
async def get_items(ids: CSVList[int] = Query(...)):
    return ids
```

A request like `GET /items?ids=1,2,3` returns `[1, 2, 3]`.

---

## Custom CSV Separator

The default separator is `,`. To change it, use `csv_separator_config` from
`fastapi_filters.configs`. See [Configuration](configuration.md#csv_separator_config) for
full details and examples.
