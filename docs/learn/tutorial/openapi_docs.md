# OpenAPI Docs

`fastapi-filters` uses CSV-separated values for list parameters (e.g., `field[in]=a,b,c`).
By default, Swagger UI may render these incorrectly with `explode: true`, generating separate
query parameters for each value.

## Fixing Swagger UI

Use `fix_docs()` to patch the OpenAPI schema so CSV parameters render correctly:

```python
from fastapi import FastAPI

from fastapi_filters.docs import fix_docs

app = FastAPI()

fix_docs(app)
```

This sets `explode: false` on the relevant parameters in the generated OpenAPI schema,
so Swagger UI displays a single input field for comma-separated values.

!!! tip

    Call `fix_docs(app)` right after creating your `FastAPI` instance, before defining any routes.
