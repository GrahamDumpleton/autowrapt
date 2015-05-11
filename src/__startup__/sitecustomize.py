'''Provides a custom 'sitecustomize' module which will be used when the
'autowrapt' wrapper script is used when launching a Python program. This
custom 'sitecustomize' module will find any existing 'sitecustomize'
module which may have been overridden and ensures that that is imported
as well. Once that is done then the monkey patches for ensuring any
bootstrapping is done for registering post import hook callback
functions after the 'usercustomize' module is loaded will be applied. If
however 'usercustomize' support is not enabled, then the registration
will be forced immediately.

'''

import os
import sys
import site
import time

_debug = os.environ.get('AUTOWRAPT_DEBUG',
        'off').lower() in ('on', 'true', '1')

def log_message(text, *args):
    if _debug:
        text = text % args
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print('AUTOWRAPT: %s (%d) - %s' % (timestamp, os.getpid(), text))

log_message('autowrapt - sitecustomize (%s)', __file__)

log_message('working_directory = %r', os.getcwd())

log_message('sys.prefix = %r', os.path.normpath(sys.prefix))

try:
    log_message('sys.real_prefix = %r', sys.real_prefix)
except AttributeError:
    pass

log_message('sys.version_info = %r', sys.version_info)
log_message('sys.executable = %r', sys.executable)

if hasattr(sys, 'flags'):
    log_message('sys.flags = %r', sys.flags)

log_message('sys.path = %r', sys.path)

# This 'sitecustomize' module will override any which may already have
# existed, be it one supplied by the user or one which has been placed
# in the 'site-packages' directory of the Python installation. We need
# to ensure that the existing 'sitecustomize' module is still loaded. To
# do that we remove the special startup directory containing this module
# from 'sys.path' and use the 'imp' module to find any original
# 'sitecustomize' module and load it.

import imp

boot_directory = os.path.dirname(__file__)
pkgs_directory = os.path.dirname(os.path.dirname(boot_directory))

log_message('pkgs_directory = %r', pkgs_directory)
log_message('boot_directory = %r', boot_directory)

path = list(sys.path)

try:
    path.remove(boot_directory)
except ValueError:
    pass

try:
    (file, pathname, description) = imp.find_module('sitecustomize', path)
except ImportError:
    pass
else:
    log_message('sitecustomize = %r', (file, pathname, description))

    imp.load_module('sitecustomize', file, pathname, description)

# Before we try and setup or trigger the bootstrapping for the
# registration of the post import hook callback functions, we need to
# make sure that we are still executing in the context of the same
# Python installation as the 'autowrapt' script was installed in. This
# is necessary because if it isn't and we were now running out of a
# different Python installation, then it may not have the 'autowrapt'
# package installed and so our attempts to import it will fail causing
# startup of the Python interpreter to fail in an obscure way.

expected_python_prefix = os.environ.get('AUTOWRAPT_PYTHON_PREFIX')
actual_python_prefix = os.path.realpath(os.path.normpath(sys.prefix))

expected_python_version = os.environ.get('AUTOWRAPT_PYTHON_VERSION')
actual_python_version = '.'.join(map(str, sys.version_info[:2]))

python_prefix_matches = expected_python_prefix == actual_python_prefix
python_version_matches = expected_python_version == actual_python_version

log_message('python_prefix_matches = %r', python_prefix_matches)
log_message('python_version_matches = %r', python_version_matches)

if python_prefix_matches and python_version_matches:
    bootstrap_packages = os.environ.get('AUTOWRAPT_BOOTSTRAP')

    log_message('bootstrap_packages = %r', bootstrap_packages)

    if bootstrap_packages:
        # When the 'autowrapt' script is run from out of a Python egg
        # directory under 'buildout', then the path to the egg directory
        # will not actually be listed in 'sys.path' as yet. This is
        # because 'buildout' sets up any scripts so that 'sys.path' is
        # specified only within the script. So that we can find the
        # 'autowrapt' package, we need to ensure that in this case the
        # egg directory for 'autowrapt' is manually added to 'sys.path'
        # before we can import it.

        pkgs_directory_missing = pkgs_directory not in sys.path

        if pkgs_directory_missing:
            sys.path.insert(0, pkgs_directory)

        from autowrapt.bootstrap import bootstrap
        from autowrapt.bootstrap import register_bootstrap_functions

        # If we had to add the egg directory above corresponding to the
        # 'autowrapt' package, now remove it to ensure the presence of
        # the directory doesn't cause any later problems. It is quite
        # possible that the directory will be added back in by scripts
        # run under 'buildout' but that would be the normal behaviour
        # and better off letting it do it how it wants to rather than
        # leave the directory in place.

        if pkgs_directory_missing:
            try:
                sys.path.remove(pkgs_directory)
            except ValueError:
                pass

        # Trigger the application of the monkey patches to the 'site'
        # module so that actual registration of the post import hook
        # callback functions is only run after any 'usercustomize'
        # module has been imported. If 'usercustomize' module support
        # is disabled, as it will be in a Python virtual environment,
        # then trigger the registration immediately.

        bootstrap()

        if not site.ENABLE_USER_SITE:
            register_bootstrap_functions()
