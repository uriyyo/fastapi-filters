# Contributing

Any and all contributions and involvement with the project is welcome. The easiest way to begin contributing is to check out the open issues on GitHub.

## Documentation

The documentation is built using [mkdocs](https://www.mkdocs.org/). All documentation is in markdown format, and can be found in `./docs/`


## Contributing Code

### Step 1: prerequisites

`fastapi-filters` uses [uv](https://docs.astral.sh/uv/) for dependency management.
Please, install uv before continuing.

Minimum supported python version is `3.10`.


### Step 2: clone the repo

```shell
git clone https://github.com/uriyyo/fastapi-filters
```


### Step 3: install dependencies

To install all dependencies, run:
```sh
uv sync --dev
```

To install docs dependencies, run:
```sh
uv sync --group docs
```

### Step 4: do your changes

If you want to add a new feature, please, create an issue first and describe your idea.

If you want to add/update docs, then you will need to edit the `./docs/` directory.
You can run the docs locally with:
```sh
uv run mkdocs serve
```

### Step 5: run pre-commit hooks

Before creating a commit, please, run pre-commit hooks:
```sh
uv run pre-commit run --all-files
```

You can also install pre-commit hooks to run automatically before each commit:
```sh
uv run pre-commit install
```

### Step 6: run tests

To run tests, run:
```sh
uv run pytest tests
```

If you want to run tests with coverage, run:
```sh
uv run pytest tests --cov=fastapi_filters
```

### Step 7: create a pull request

After you have done all changes, please, create a pull request.
