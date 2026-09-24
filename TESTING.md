# Testing

## Where the tests are

Tests live in the [tests/](tests/) directory at the top of the repository,
separate from the package code in src/autowrapt/. Test files are named
`test_*.py` and are discovered by pytest, which is configured via the
`[tool.pytest.ini_options]` section of [pyproject.toml](pyproject.toml).

## How the tests work

Everything autowrapt does happens at interpreter startup, driven by the
autowrapt-init.start and autowrapt-init.pth files installed at the top of
site-packages. An editable install, which is what the project environment
holds, does not exercise those files the way a user's install does. The
tests therefore work on the real thing:

- A session scoped fixture in [tests/conftest.py](tests/conftest.py)
  builds the wheel from the working tree with `uv build`.

- A second fixture creates a fresh virtual environment with `uv venv`,
  using the same Python the tests run under, and installs the wheel into
  it with `uv pip install`. That pulls wrapt from PyPI or the uv cache, so
  the first run needs network access.

- Each test then runs a snippet of code in a new interpreter from that
  environment, with the AUTOWRAPT_BOOTSTRAP variable set or unset as the
  test requires, and checks what was printed. The example hook shipped in
  the package, registered under the autowrapt.examples entry point group,
  is what the tests trigger.

Building and installing happens once per session, so the suite takes a few
seconds rather than a few minutes. The `uv` command must be on the PATH.

## Running the tests

All tooling in this project goes through [uv](https://docs.astral.sh/uv/),
which manages the project environment and installs the package and its
development dependencies (including pytest) automatically.

The simplest way to run the test suite is via the Justfile target:

```console
just test
```

Extra arguments are passed through to pytest, for example:

```console
just test -v
just test tests/test_bootstrap.py
just test -k variable
```

Equivalently, run pytest directly with uv:

```console
uv run pytest
```

## Testing across Python versions

The project supports the same Python versions as wrapt, including the free
threaded builds of 3.13, 3.14 and 3.15. The supported list is defined at
the top of the [Justfile](Justfile). The default version used by plain
`just test` is pinned in [.python-version](.python-version).

Run the test suite on every supported version:

```console
just test-all
```

Run the test suite on one nominated version:

```console
just test-python 3.9
just test-python 3.14t
```

Extra arguments are passed through to pytest for these targets too. uv
downloads any Python version it does not already have, and each version
gets its own environment (.venv-VERSION) so the default .venv is left
untouched.

## Writing tests

- Put new test files in tests/ and name them `test_*.py`.

- Anything about startup behaviour goes through the `run_python` fixture,
  which runs code in the installed environment's interpreter. Pass
  `variable=` to set AUTOWRAPT_BOOTSTRAP for that run, and `options=` for
  interpreter flags such as `-S`. Assert on the printed output.

- Tests of the package as imported in the project environment, such as
  the version check, can simply `import autowrapt`.

- Tests should not depend on anything in the scratch/ directory, which is
  not part of the repository.
