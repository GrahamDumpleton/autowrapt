"""The behaviour of the installed package at interpreter startup, exercised
by running a fresh interpreter from a virtual environment with the wheel
installed. See conftest.py for the fixtures."""

from conftest import RunPython

EXTRA_LINE = "The wrapt package is absolutely amazing and you should use it."
ZEN_TITLE = "The Zen of Python, by Tim Peters"

CHECK_PTH_FILE = """
import os
import sysconfig

path = os.path.join(sysconfig.get_paths()["purelib"], "autowrapt-init.pth")

print(os.path.exists(path))
"""

CHECK_AUTOWRAPT_IMPORTED = """
import sys

import this

names = [name for name in sys.modules if name.split(".")[0] == "autowrapt"]

print(bool(names))
"""

CHECK_PACKAGE_IMPORTS = """
import sys

before = set(sys.modules)

import autowrapt
import autowrapt.bootstrap

print(sorted(set(sys.modules) - before))
"""

CHECK_BOOTSTRAP_IDEMPOTENT = """
import site

import autowrapt.bootstrap

before = site.execsitecustomize

autowrapt.bootstrap.bootstrap()

print(site.execsitecustomize is before)
"""


def test_pth_file_installed_in_site_packages(run_python: RunPython) -> None:
    result = run_python(CHECK_PTH_FILE)

    assert result.stdout.strip() == "True"


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
    result = run_python(CHECK_AUTOWRAPT_IMPORTED)

    assert EXTRA_LINE not in result.stdout
    assert result.stdout.splitlines()[-1] == "False"


def test_nothing_happens_when_variable_empty(run_python: RunPython) -> None:
    result = run_python(CHECK_AUTOWRAPT_IMPORTED, variable="")

    assert EXTRA_LINE not in result.stdout
    assert result.stdout.splitlines()[-1] == "False"


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
    # The .pth file imports the package at startup, so importing it must
    # pull in nothing beyond its own modules. In particular wrapt is only
    # imported once registration runs.

    result = run_python(CHECK_PACKAGE_IMPORTS)

    assert result.stdout.strip() == "['autowrapt', 'autowrapt.bootstrap']"


def test_bootstrap_is_idempotent(run_python: RunPython) -> None:
    # bootstrap() has already run from the .pth file, so a second call must
    # not wrap the site functions again.

    result = run_python(CHECK_BOOTSTRAP_IDEMPOTENT, variable="autowrapt.examples")

    assert result.stdout.splitlines()[-1] == "True"
