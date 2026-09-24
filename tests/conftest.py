"""Fixtures which build the wheel and install it into a fresh virtual
environment, so the tests exercise the autowrapt-init.pth file exactly as
it is installed for users. The environment pytest itself runs in holds an
editable install of the project, which is not what a user gets.
"""

import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Optional

import pytest

ROOT = Path(__file__).resolve().parent.parent

RunPython = Callable[..., "subprocess.CompletedProcess[str]"]


def _run(command: Sequence[str]) -> "subprocess.CompletedProcess[str]":
    result = subprocess.run(list(command), capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    return result


def _uv() -> str:
    uv = shutil.which("uv")

    if uv is None:
        raise RuntimeError("uv is required to build and install the wheel")

    return uv


@pytest.fixture(scope="session")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The autowrapt wheel built from the working tree."""

    out_dir = tmp_path_factory.mktemp("dist")

    _run([_uv(), "build", "--wheel", "--out-dir", str(out_dir), str(ROOT)])

    [path] = out_dir.glob("autowrapt-*.whl")

    return path


@pytest.fixture(scope="session")
def venv_python(wheel: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The interpreter of a fresh virtual environment, created with the
    same Python the tests run under, with the wheel installed into it."""

    venv = tmp_path_factory.mktemp("env") / "venv"
    base = getattr(sys, "_base_executable", sys.executable)

    _run([_uv(), "venv", "--python", base, str(venv)])

    if os.name == "nt":
        python = venv / "Scripts" / "python.exe"
    else:
        python = venv / "bin" / "python"

    _run([_uv(), "pip", "install", "--python", str(python), str(wheel)])

    return python


@pytest.fixture(scope="session")
def run_python(venv_python: Path) -> RunPython:
    """Run a snippet of code in the virtual environment's interpreter.

    The AUTOWRAPT_BOOTSTRAP variable is set to `variable` when that is
    given and is otherwise absent, whatever the outer environment has.
    Extra interpreter options go in `options`.
    """

    def run(
        code: str,
        *,
        variable: Optional[str] = None,
        options: Sequence[str] = (),
    ) -> "subprocess.CompletedProcess[str]":
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in ("AUTOWRAPT_BOOTSTRAP", "PYTHONPATH")
        }

        if variable is not None:
            env["AUTOWRAPT_BOOTSTRAP"] = variable

        result = subprocess.run(
            [str(venv_python), *options, "-c", code],
            env=env,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr

        return result

    return run
