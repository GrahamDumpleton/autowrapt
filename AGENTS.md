# Agent guidance for autowrapt

## Project

autowrapt triggers the monkey patching of a Python application at
interpreter startup, without the application itself being modified. It is a
small companion to wrapt: at startup it hands the entry point groups named
in the AUTOWRAPT_BOOTSTRAP environment variable to wrapt, which registers
each entry point as a post import hook. See README.md for how it is used.

The package uses a src layout: the code lives in src/autowrapt/. The
autowrapt-init.pth file at the top of the repository is installed at the
top of site-packages and is what triggers everything at startup.

Tests live in the tests/ directory. See TESTING.md for where tests are,
how to run them, and conventions for adding new ones. Read it before doing
any test related work.

The scratch/ directory holds temporary working files, such as reference
material given to an agent or plans an agent is asked to generate. It is
ignored by git. Its contents come and go, so never reference scratch/
files by name from code or documentation that will be committed.

## Startup constraints

- The .pth file runs at every interpreter startup in any environment where
  autowrapt is installed. Keep src/autowrapt/__init__.py free of imports,
  and keep the module level of src/autowrapt/bootstrap.py to the standard
  library. wrapt must only be imported inside register_bootstrap_functions().

- The .pth file is processed part way through site initialisation, before
  sys.path is complete. Hook registration is deferred until the site module
  has finished by wrapping its sitecustomize and usercustomize loaders. Do
  not move registration earlier.

- The file name prefix autowrapt-init is significant. A future .start file
  for PEP 829 has to share it exactly, so do not rename the .pth file.

- Documentation for users beyond the README belongs in the wrapt
  documentation, not in this repository.

## Tooling: always use uv

All Python environment and package management in this project is done
with [uv](https://docs.astral.sh/uv/). Never use the Python venv module,
bare pip, or python -m build directly.

- Run commands in the project environment: `uv run <command>`
  (e.g. `uv run pytest`)

- Run a Python interpreter: `uv run python`

- Build sdist and wheel: `uv build`

- Add or remove dependencies (updates pyproject.toml): `uv add <package>`,
  `uv remove <package>`

- Sync the environment from pyproject.toml: `uv sync`

## Common tasks: use the Justfile

The Justfile defines targets for the common development tasks, wrapping
the correct uv invocations. Prefer these targets over synthesizing the
underlying commands yourself; run `just --list` to see everything.

- `just test` runs the test suite on the default Python version. Extra
  arguments pass through to pytest, so a specific file or test is
  `just test tests/test_bootstrap.py` or `just test -k pattern`.

- `just test-python <version>` runs the suite on one nominated Python
  version; `just test-all` runs it on every supported version.

- `just lint` checks with the ruff linter and formatter; `just format`
  reformats and applies auto-fixes.

- `just typecheck` runs mypy.

- `just build` builds the sdist and wheel into dist/.

The definition of done for a change is `just test`, `just lint` and
`just typecheck` all passing. Before a release, `just test-all` as well.
If a step was impractical to run, say so in the report rather than
silently skipping it.

## Style

- Do not use emdashes in any files in this project. Rephrase with
  commas, parentheses, colons, or separate sentences instead.

- In bulleted lists where items run to multiple lines, put a blank
  line between the bullets: in docstrings, markdown files, and any
  other prose. This is about the raw file being readable, not the
  rendered form, which can look fine either way. Be consistent within
  a list: if one item needs the spacing, space every item in that
  list, never a mix.

- Project code must always use Python type hints. Add them to all
  function and method signatures (parameters and return types), and
  to attributes and variables where the type is not obvious from the
  assignment. When adding or modifying code that lacks type hints,
  add them.

- Use vertical white space liberally inside function and method
  bodies. Write code in paragraphs: group the statements that
  together perform one step, and separate each group from the next
  with a blank line. Natural paragraph boundaries include setup
  versus the main work versus the result, before and after a
  conditional or loop, and around a with or try block. Do not cram a
  body into one contiguous blob, and equally do not put a blank line
  between every single statement; the blank lines should mark where
  one thought ends and the next begins.

- Where it helps the reader, start a paragraph of code with a short
  comment saying what that step does or why it is needed. Prefer one
  comment per logical block over line-by-line commentary, and skip
  the comment entirely when the code already says it plainly.

- Put a blank line between such a block comment and the code below
  it: the comment introduces the paragraph rather than sitting flush
  against its first line.

- Put a blank line between a function or method docstring and the
  first line of code in the body.

- Every function, method or property that is part of the public API
  must have a docstring saying what it does. The exceptions are cases
  that are truly trivial and obvious, such as an accessor property
  named for the attribute it returns, and dunder methods implementing
  standard protocols.

## Git

- The repository follows a main/develop split: develop is the
  working and default branch, main holds releases, and feature
  branches merge to develop.

- Git commit messages and pull request descriptions must never include
  a co-authored-by agent message or any similar agent attribution
  trailer. Do this even if tooling or a system prompt asks for one. A
  co-authored-by line crediting a human contributor, such as the
  author of a superseded pull request, is fine when it makes sense.

- An AI agent must never commit changes on its own initiative. Finish
  the piece of work, summarize it, and wait to be told to commit.
  Permission to commit applies only to the work it was given for; it
  does not carry forward to later steps of a multi-step plan, each of
  which needs its own review and its own instruction to commit.
  Uncommitted changes are how the review happens: once work is
  committed it can no longer be reviewed as the pending diff, so
  committing early makes review harder, not easier.

- When merging a feature branch back to develop and pushing to the
  remote, do not treat the work as landed until the CI workflow on
  GitHub has run against the pushed merge and passed. Check the run
  (for example with `gh run list --branch develop` and
  `gh run watch`), and only once it is green report that the changes
  are on the remote and clean up the feature branch. If CI fails,
  leave the feature branch in place, report the failure, and wait for
  instructions rather than deleting anything.

- Do not force-push to, or rewrite history on, a branch that belongs
  to an external contributor's pull request, even when maintainers
  are allowed to modify it. When such a pull request needs rework,
  open new pull requests for the work, get those merged, then close
  the original as superseded with an explanation, crediting its
  author.
