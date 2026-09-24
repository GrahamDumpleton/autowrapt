"""Functions run at interpreter startup to register the post import hooks
named in the AUTOWRAPT_BOOTSTRAP environment variable. This module is
imported by autowrapt.init(), the entry point named in the startup files
installed at the top of site-packages, and only once that has found the
variable set.

Nothing beyond the standard library may be imported at module level here.
On Python 3.14 and earlier this module is imported part way through site
initialisation, when sys.path may not yet be complete, and wrapt itself is
only imported once registration runs.
"""

import os
import site

# The type annotations below must not cost an import at startup, so the
# typing machinery is only imported for the type checker.

TYPE_CHECKING = False

if TYPE_CHECKING:
    from collections.abc import Callable

_registered = False


def register_bootstrap_functions() -> None:
    """Discover and register the post import hooks for every entry point
    group named in the AUTOWRAPT_BOOTSTRAP environment variable. The value
    is a comma separated list of group names.
    """

    # Registration must only ever happen once, however many times this is
    # called during startup.

    global _registered

    if _registered:
        return

    _registered = True

    # It is safe to import wrapt at this point, as this runs after every
    # module search directory has been added to sys.path.

    from wrapt import discover_post_import_hooks

    for name in os.environ.get("AUTOWRAPT_BOOTSTRAP", "").split(","):
        name = name.strip()

        if name:
            discover_post_import_hooks(name)


def _execsitecustomize_wrapper(wrapped: "Callable[[], None]") -> "Callable[[], None]":
    def _execsitecustomize() -> None:
        try:
            wrapped()
        finally:
            # When usercustomize support is disabled, as it is in a virtual
            # environment, loading sitecustomize is the last step of site
            # initialisation, so registration has to happen here instead.

            if not site.ENABLE_USER_SITE:
                register_bootstrap_functions()

    return _execsitecustomize


def _execusercustomize_wrapper(wrapped: "Callable[[], None]") -> "Callable[[], None]":
    def _execusercustomize() -> None:
        try:
            wrapped()
        finally:
            register_bootstrap_functions()

    return _execusercustomize


_patched = False


def bootstrap() -> None:
    """Arrange for the post import hooks to be registered as the last step
    of site initialisation, once the module search path is complete. This is
    what autowrapt.init() calls when AUTOWRAPT_BOOTSTRAP is set.
    """

    global _patched

    if _patched:
        return

    _patched = True

    # On Python 3.14 and earlier the .pth file is processed part way through
    # site initialisation, and other .pth files, possibly including one which
    # makes wrapt importable, may not have been processed yet. Registration
    # is therefore deferred to the last thing the site module does, which is
    # loading the sitecustomize module, or the usercustomize module when
    # support for that is enabled. Both loaders are wrapped, with the
    # sitecustomize wrapper only acting when usercustomize support is
    # disabled. On Python 3.15 and later the .start entry point only runs
    # once every path extension has been applied, so the deferral is not
    # needed there, but it is kept so that every version behaves the same.
    #
    # wrapt cannot be used for this wrapping, for the same reason it cannot
    # be imported yet, so plain function wrappers are used instead.

    site.execsitecustomize = _execsitecustomize_wrapper(site.execsitecustomize)
    site.execusercustomize = _execusercustomize_wrapper(site.execusercustomize)
