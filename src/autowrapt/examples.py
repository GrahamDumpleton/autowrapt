"""An example post import hook, registered under the autowrapt.examples
entry point group against the this module. With AUTOWRAPT_BOOTSTRAP set to
autowrapt.examples, importing this prints the Zen of Python as usual, then
one extra line.
"""

from types import ModuleType


def autowrapt_this(module: ModuleType) -> None:
    """Post import hook for the this module."""

    print("The wrapt package is absolutely amazing and you should use it.")
