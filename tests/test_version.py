from importlib.metadata import version
from pathlib import Path

import autowrapt


def test_version_matches_package_metadata() -> None:
    assert autowrapt.__version__ == version("autowrapt")


def test_version_matches_wheel(wheel: Path) -> None:
    assert wheel.name.startswith(f"autowrapt-{autowrapt.__version__}-")
