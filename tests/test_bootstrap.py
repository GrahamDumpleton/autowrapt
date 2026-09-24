"""The behaviour of the installed package at interpreter startup, exercised
by running a fresh interpreter from a virtual environment with the wheel
installed. See conftest.py for the fixtures."""

import sys

import pytest
from conftest import RunPython

EXTRA_LINE = "The wrapt package is absolutely amazing and you should use it."
ZEN_TITLE = "The Zen of Python, by Tim Peters"

CHECK_STARTUP_FILES = """
import os
import sysconfig

purelib = sysconfig.get_paths()["purelib"]

for name in ("autowrapt-init.pth", "autowrapt-init.start"):
    print(name, os.path.exists(os.path.join(purelib, name)))
"""

CHECK_MODULES_LOADED = """
import sys

import this

names = [name for name in sys.modules if name.split(".")[0] in ("autowrapt", "wrapt")]

print(sorted(names))
"""

# The package is already loaded by the startup files, so it is dropped from
# sys.modules first to measure what importing it afresh pulls in.

CHECK_INIT_IMPORTS = """
import sys

for name in list(sys.modules):
    if name.split(".")[0] == "autowrapt":
        del sys.modules[name]

before = set(sys.modules)

import autowrapt

print(sorted(set(sys.modules) - before))
"""

CHECK_PACKAGE_IMPORTS = """
import sys

for name in list(sys.modules):
    if name.split(".")[0] == "autowrapt":
        del sys.modules[name]

before = set(sys.modules)

import autowrapt
import autowrapt.bootstrap

print(sorted(set(sys.modules) - before))
"""

CHECK_INIT_IDEMPOTENT = """
import site

import autowrapt
import autowrapt.bootstrap

before = site.execsitecustomize

autowrapt.init()
autowrapt.bootstrap.bootstrap()

print(site.execsitecustomize is before)
"""

ENTRY_POINT_EXECUTED = "Executing entry point: autowrapt:init from "
IMPORT_LINES_SUPPRESSED = "autowrapt-init.pth are suppressed due to matching "
IMPORT_LINES_DEPRECATED = "autowrapt-init.pth are deprecated, "


def test_startup_files_installed_in_site_packages(run_python: RunPython) -> None:
    result = run_python(CHECK_STARTUP_FILES)

    assert result.stdout.splitlines() == [
        "autowrapt-init.pth True",
        "autowrapt-init.start True",
    ]


def test_hook_fires_when_variable_set(run_python: RunPython) -> None:
    result = run_python("import this", variable="autowrapt.examples")

    lines = result.stdout.splitlines()

    assert lines[0] == ZEN_TITLE
    assert lines[-1] == EXTRA_LINE


def test_hook_waits_for_the_import(run_python: RunPython) -> None:
    # A post import hook only runs when its module is imported. Registering
    # it at startup must not import the module.

    result = run_python(
        "import sys; print('this' in sys.modules)", variable="autowrapt.examples"
    )

    assert result.stdout.strip() == "False"


def test_nothing_happens_when_variable_unset(run_python: RunPython) -> None:
    # The startup files always import the package and call init(), so the
    # package itself is loaded, but nothing beyond it.

    result = run_python(CHECK_MODULES_LOADED)

    assert EXTRA_LINE not in result.stdout
    assert result.stdout.splitlines()[-1] == "['autowrapt']"


def test_nothing_happens_when_variable_empty(run_python: RunPython) -> None:
    result = run_python(CHECK_MODULES_LOADED, variable="")

    assert EXTRA_LINE not in result.stdout
    assert result.stdout.splitlines()[-1] == "['autowrapt']"


def test_multiple_groups_with_whitespace(run_python: RunPython) -> None:
    # Unknown groups are harmless, and whitespace around names is ignored.

    result = run_python("import this", variable="no.such.group, autowrapt.examples ,")

    assert result.stdout.splitlines()[-1] == EXTRA_LINE


def test_nothing_happens_without_site(run_python: RunPython) -> None:
    # With -S the site module is not run, so the .pth file is never seen.

    result = run_python("import this", variable="autowrapt.examples", options=["-S"])

    assert result.stdout.splitlines()[0] == ZEN_TITLE
    assert EXTRA_LINE not in result.stdout


def test_package_import_is_light(run_python: RunPython) -> None:
    # The startup files import the package at every startup, so importing
    # it must pull in nothing at all, and importing autowrapt.bootstrap must
    # pull in nothing beyond itself. In particular wrapt is only imported
    # once registration runs.

    result = run_python(CHECK_INIT_IMPORTS)

    assert result.stdout.strip() == "['autowrapt']"

    result = run_python(CHECK_PACKAGE_IMPORTS)

    assert result.stdout.strip() == "['autowrapt', 'autowrapt.bootstrap']"


def test_init_is_idempotent(run_python: RunPython) -> None:
    # init() has already run from the startup files, so calling it again,
    # or calling bootstrap() directly, must not wrap the site functions
    # again.

    result = run_python(CHECK_INIT_IDEMPOTENT, variable="autowrapt.examples")

    assert result.stdout.splitlines()[-1] == "True"


@pytest.mark.skipif(sys.version_info < (3, 15), reason="PEP 829 needs Python 3.15")
def test_start_file_used_and_pth_line_suppressed(run_python: RunPython) -> None:
    # On Python 3.15 and later the site module reports under -v that it
    # executed the entry point from the .start file and suppressed the
    # import line in the .pth file, and the hook still fires.

    result = run_python("import this", variable="autowrapt.examples", options=["-v"])

    assert ENTRY_POINT_EXECUTED in result.stderr
    assert IMPORT_LINES_SUPPRESSED in result.stderr
    assert IMPORT_LINES_DEPRECATED not in result.stderr
    assert result.stdout.splitlines()[-1] == EXTRA_LINE
