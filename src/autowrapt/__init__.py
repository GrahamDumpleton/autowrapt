"""Bootstrap mechanism for monkey patches.

autowrapt triggers the monkey patching of a Python application at
interpreter startup, without the application itself being modified. The
entry point groups named in the AUTOWRAPT_BOOTSTRAP environment variable
are handed to wrapt, which registers each entry point as a post import
hook for the module it names.
"""

# The autowrapt-init.pth file imports autowrapt.bootstrap at interpreter
# startup, so this module holds nothing but the version. Do not add
# imports here.


def _format_version(parts: "tuple[str, ...]") -> str:
    base = ".".join(parts[:3])

    if len(parts) == 3:
        return base

    suffix = parts[3]

    return (
        f"{base}.{suffix}" if suffix.startswith(("dev", "post")) else f"{base}{suffix}"
    )


__version_info__ = ("2", "0", "0", "rc1")
__version__ = _format_version(__version_info__)
