# Roadmap

## Initial idea

Roughly 4 years ago I had a task that required to create a lot of endpoints
with similar filtering/sorting logic.
While I was working on it I decided to actually create this library
to avoid copy-pasting the same code over and over again.

## Original plan

Initially I planned to create a small library that will provide low-level API
on how to create filters and sorters and then to be able to implement
some higher-level API on top of it.

## What went wrong

But everything went wrong when I added `FilterSet` feature.
It was too early to add it and core functionality was not ready yet,
so I had to change a lot of code to make it work and as a result
I ended up with a library that is not very flexible and `FilterSet` logic
is limited because declaration level was written from scratch
and was not built on top of `pydantic` or other libraries
that are already doing similar things.

It resulted in a lot of code that handles typing introspection and validation,
there are a lot of edge cases that are not handled
and it is not very easy to maintain,
and why should I do it if there are already libraries
that do the same thing but better?

## What I imagine a good library should look like

### Low-level API and flat filters (Phase 1)

First of all I wanted to create a library with easy integration with `fastapi`
that will allow you to add filtering and sorting to your endpoints
with minimal code and configuration.
I like how it looks now but there is still room for improvement,
for instance I would like to bundle sorting and filtering spec into one object,
so you will be able to declare something like this:

```python
@app.get("/items")
async def get_items(
    spec: Annotated[
        QuerySpec,
        Depends(
            create_query_spec(
                filters=create_filters(
                    name=str,
                    price=int,
                ),
                sorters=create_sorters(
                    name=str,
                    price=int,
                ),
            )
        )
    ],
):
    ...
    query = apply_spec(query, spec)
```

Filtering and sorting are fundamentally different operations —
filters reduce the result set (WHERE), sorters order it (ORDER BY).
They have different representations, compilation logic, and operators,
so they should be separate objects at the core level:
`FilterSpec` and `SorterSpec` with their own creation functions.

`QuerySpec` is a thin convenience wrapper that bundles both together.
The `spec` object will have `filters` and `sorters` attributes
that will contain the parsed filters and sorters from the query parameters.
In many cases you want to bundle them together and it will be
more convenient to have them in one object instead of having
separate dependencies for filters and sorters.

But still there should be a way to use them separately if you don't want
to use `QuerySpec` and just want to use `create_filters`
or `create_sorters` directly:

```python
@app.get("/items")
async def get_items(
    filters: Annotated[FilterSpec, Depends(create_filters(name=str, price=int))],
    sorters: Annotated[SorterSpec, Depends(create_sorters(name=str, price=int))],
):
    ...
```

Both `create_filters` and `create_sorters` should be resolved
into their respective spec objects and then can be passed down
the road to the function that will apply them to the query.

Flat filters should be something simple that will allow you to pass filters
as just a list of things to filter by, for instance something like this:

```
/items?name=foo&price[ge]=10&price[le]=100
```

Also you should be able to apply the same operator to the same field
multiple times, for instance something like this:

```
/items?name[ne]=foo&name[ne]=bar
```

### AST and compiler (Phase 2)

To support more advanced filtering we will need to have some way to represent
filters as AST and then have a compiler layer that will compile
this AST into something that can be applied to the query,
for instance SQLAlchemy query or Django ORM query or something else.

Structure that I imagine for this AST is something like this:

```python
@dataclass
class Node:
    pass

@dataclass
class ExprNode[T=Any](Node):
    field: str
    operator: str
    value: T

@dataclass
class GroupNode(Node):
    type: str  # "and" or "or", maybe something else in the future
    nodes: Sequence[Node]

@dataclass
class NegationNode(Node):
    node: Node
```

And abstract compiler might look like this:

```python
class QueryCompiler(ABC, Generic[T]):
    def compile(self, node: Node) -> T:
        match node:
            case ExprNode():
                return self.compile_expr(node)
            case GroupNode():
                return self.compile_group(node)
            case NegationNode():
                return self.compile_negation(node)
            case _:
                raise ValueError(f"Unknown node type: {type(node)}")

    @abstractmethod
    def compile_expr(self, node: ExprNode) -> T:
        pass

    @abstractmethod
    def compile_group(self, node: GroupNode) -> T:
        pass

    @abstractmethod
    def compile_negation(self, node: NegationNode) -> T:
        pass
```

### Class-based declaration (Phase 3)

Class-based declaration of filters and sorters should be added as well,
it's a nice way to combine several filters/sorters together and reuse them
in different endpoints, for instance you can declare `ItemFilterSet`
that will contain filters for `Item` model and then use it
in different endpoints that work with `Item` model.
As another example some common filters/sorters that are used
in different endpoints can be declared in one class and then reused,
for instance something like `IDQuerySet` that will contain filter
for `id` field and then you can use it in different endpoints
that work with different models but have `id` field.
And then you can easily add it to other query sets to extend them
with `id` filter without having to declare it again.

```python
class IDQuerySet(QuerySet):
    id: QueryField[UUID]

class ItemQuerySet(IDQuerySet):  # Inherit from IDQuerySet to get id filter for free
    name: QueryField[str]
    price: QueryField[int]
```

Or to have some way to merge `QuerySet` together,
like for instance overriding `|` operator to merge two `QuerySet` together,
so you can do something like this:

```python
def get_items(
    filters: Annotated[
        QuerySpec,
        Depends(ItemQuerySet | IDQuerySet),
    ],
):
    ...
```

And then also, there should be a way to incorporate sorters
into `QuerySet` as well, I imagine something like this:

```python
class ItemQuerySet(QuerySet):
    name: QueryField[str]
    price: QueryField[int]

    @classmethod
    def sorters(cls) -> SorterSpec:
        return SorterSpec(
            [nulllast(cls.name), cls.price],
            default=-cls.name,
        )
```

Or to have some way to introspect sorters from `QuerySet` as well,
so you can do something like this:

```python
class ItemQuerySet(QuerySet):
    name: QueryField[str] = query_field(sort=True)
    price: QueryField[int] = query_field(sort=True)
```

But again `QuerySet` or `FilterSet` how it's named now is something optional
and higher-level API, you should be able to use low-level API without it
if you don't want to use it, for instance you can just use `create_filters`
and `create_sorters` directly without having to declare any classes,
everything should be built on top of low-level API
and not the other way around, so you can choose what level of abstraction
you want to use and not be forced to use something that you don't need.

### Relationship support + additional frameworks (Phase 4)

Relationship/join traversal should allow filtering across related models.
This is a commonly needed feature and should work with both
the low-level API and the class-based `QuerySet` declaration.

For the low-level API it could look something like this:

```python
create_filters(
    category__name=str,
    category__id=int,
)
```

And for the class-based API:

```python
class ItemQuerySet(QuerySet):
    name: QueryField[str]
    category__name: QueryField[str]
    category__id: QueryField[int]
```

The compiler should handle automatic join generation
when it encounters relationship paths.

Additionally, the compiler abstraction from Phase 2 should be proven
by implementing support for other frameworks like Django ORM,
Tortoise ORM, etc.

### Complex JSON filters + custom query language (Phase 5)

Complex filters might be used as POST (QUERY) body
and will allow you to pass more complex filters,
for instance something like this:

```json
[
  {
    "type": "and",
    "filters": [
      {
        "field": "name",
        "op": "eq",
        "value": "foo"
      },
      {
        "type": "or",
        "filters": [
          {
            "field": "price",
            "op": "ge",
            "value": 10
          },
          {
            "field": "price",
            "op": "le",
            "value": 100
          }
        ]
      }
    ]
  }
]
```

It might sound too complicated and maybe it's not worth adding,
because in many cases flat filters are enough and they are much easier
to implement and maintain, but still it's something that I want to have
in the library as well, because it will allow to cover more use cases
and be more flexible.

Another idea is to have some custom query language
that will allow to express more complex queries in a more concise way,
for instance something like this:

```
/items?q=name=='foo' and price >= 10 and price <= 100
```

The idea was to have Python AST subset as a query language,
so you can use Python syntax to express your queries and then parse it
using Python native tools like `ast` module, convert it into internal
AST representation and then compile it using the same compiler
that is described in the AST section.

With flexible core system it should be possible to implement this feature
as well without much trouble, but again it's something that I want to have
in the library but it's not a must-have feature and it can be added later
if there will be demand for it.

## Implementation plan

### Phase 1 — Low-level core + simple FastAPI integration

- Low-level API: `create_filters`, `create_sorters`
- Flat filters support (query parameters)
- Simple FastAPI integration via `Depends`
- `QuerySpec` object that bundles filters and sorters together

### Phase 2 — AST + compiler (SQLAlchemy)

- AST representation for filters (`Node`, `ExprNode`, `GroupNode`, `NegationNode`)
- Abstract `QueryCompiler` interface
- SQLAlchemy compiler implementation
- Support for applying the same operator to the same field multiple times

### Phase 3 — Class-based declaration + full FastAPI integration

- `QuerySet` class-based declaration of filters and sorters
- `QuerySet` composition via `|` operator or inheritance
- Sorters integration into `QuerySet`
- Full FastAPI integration with `QuerySet`

### Phase 4 — Relationship support + additional frameworks

- Relationship/join traversal for filtering across related models
- Integration with other frameworks (Django ORM, Tortoise ORM, etc.)

### Phase 5 — Complex JSON filters + custom query language

- Support for complex/nested filters via POST (QUERY) body
- Custom query language (python syntax subset or maybe something else)

## What next?

This doc is not like a classical ROADMAP that has clear steps and milestones,
but the phase breakdown above should give a rough idea of the order.
I will try to break each phase down into smaller steps
that can be implemented independently
and then we will see how it goes.

Hope I won't abandon this project like I did last time,
but again no promises, because I don't want to put too much pressure
on myself and I want to have fun while working on this project,
so we will see how it goes.
