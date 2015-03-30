import os
import site

from wrapt import wrap_function_wrapper, discover_post_import_hooks

_registered = False

def _register_bootstrap_functions():
    # This should in practice only ever be called once, but protect
    # outselves just in case it is somehow called a second time.

    global _registered

    if _registered:
        return 

    _registered = True

    # Now discover and register all post import hooks named in the
    # AUTOWRAPT_BOOTSTRAP environment variable. The value of the
    # environment variable must be a comma separated list.

    for name in os.environ.get('AUTOWRAPT_BOOTSTRAP', '').split(','):
        discover_post_import_hooks(name)

def _execsitecustomize(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)
    finally:
        # Check whether 'usercustomize' support is actually disabled.
        # In that case we do our work after 'sitecustomize' is loaded.

        if not site.ENABLE_USER_SITE:
            _register_bootstrap_functions()

def _execusercustomize(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)
    finally:
        _register_bootstrap_functions()

def bootstrap():
    # We want to do our real work as the very last thing in the 'site'
    # module when it is being imported so that the module search path is
    # initialised properly. What is the last thing executed depends on
    # whether 'usercustomize' module support is enabled. Such support
    # will not be enabled in Python virtual enviromments. We therefore
    # wrap the functions for the loading of both the 'sitecustomize' and
    # 'usercustomize' modules but detect when 'usercustomize' support is
    # disabled and in that case do what we need to after 'sitecustomize'
    # is loaded.

    wrapt_function_wrapper(site, 'execsitecustomize', _execsitecustomize)
    wrapt_function_wrapper(site, 'execusercustomize', _execusercustomize)
