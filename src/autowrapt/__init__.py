"""Bootstrap mechanism for monkey patches.

autowrapt triggers the monkey patching of a Python application at
interpreter startup, without the application itself being modified. The
entry point groups named in the AUTOWRAPT_BOOTSTRAP environment variable
are handed to wrapt, which registers each entry point as a post import
hook for the module it names.
"""

# This module is imported at every interpreter startup in any environment
# where autowrapt is installed, from the autowrapt-init.start file on Python
# 3.15 and later and from the autowrapt-init.pth file before that. It must
# not import anything at module level, so that when AUTOWRAPT_BOOTSTRAP is
# not set the cost of autowrapt being installed is loading this one file.


def _format_version(parts: "tuple[str, ...]") -> str:
    base = ".".join(parts[:3])

    if len(parts) == 3:
        return base

    suffix = parts[3]

    return (
        f"{base}.{suffix}" if suffix.startswith(("dev", "post")) else f"{base}{suffix}"
    )


__version_info__ = ("2", "0", "0")
__version__ = _format_version(__version_info__)


def init() -> None:
    """The startup entry point named in the autowrapt-init.start and
    autowrapt-init.pth files. Does nothing unless the AUTOWRAPT_BOOTSTRAP
    environment variable is set, and otherwise hands over to
    autowrapt.bootstrap to arrange registration of the post import hooks.
    """

    # The check on the environment variable is made here, rather than in
    # the startup files, because a .start file can only name a callable.
    # It is made before autowrapt.bootstrap is imported so that nothing
    # else is loaded when autowrapt is not in use. The os module is
    # already loaded by the site module, so importing it costs nothing.

    import os

    if not os.environ.get("AUTOWRAPT_BOOTSTRAP"):
        return

    from .bootstrap import bootstrap

    bootstrap()
