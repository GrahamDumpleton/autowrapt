'''Implements a wrapper script for executing a Python program from the
command line and which implements an alternate way of bootstrapping the
registration of post import hook callback functions when the '.pth' file
mechanism doesn't work. This can be necessary when using 'buildout' but
may still fail with 'buildout' if 'buildout' has been setup itself to
override any 'sitecustomize' module with it ignoring any existing one.

The wrapper script works by adding a special directory into the
'PYTHONPATH' environment variable, describing additional Python module
search directories, which contains a custom 'sitecustomize' module. When
the Python interpreter is started that custom 'sitecustomize' module
will be automatically loaded. This allows the custom 'sitecustomize'
file to then load any original 'sitecustomize' file which may have been
hidden and then bootstrap the registration of the post import hook
callback functions.

'''

import sys
import os
import time

_debug = os.environ.get('AUTOWRAPT_DEBUG',
        'off').lower() in ('on', 'true', '1')

def log_message(text, *args):
    if _debug:
        text = text % args
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print('AUTOWRAPT: %s (%d) - %s' % (timestamp, os.getpid(), text))

def run_program(args):
    log_message('autowrapt - wrapper (%s)', __file__)

    log_message('working_directory = %r', os.getcwd())
    log_message('current_command = %r', sys.argv)

    log_message('sys.prefix = %r', os.path.normpath(sys.prefix))

    try:
        log_message('sys.real_prefix = %r', sys.real_prefix)
    except AttributeError:
        pass

    log_message('sys.version_info = %r', sys.version_info)
    log_message('sys.executable = %r', sys.executable)
    log_message('sys.flags = %r', sys.flags)
    log_message('sys.path = %r', sys.path)

    # Determine the location of the special bootstrap directory. Add
    # this into the 'PYTHONPATH' environment variable, preserving any
    # existing value the 'PYTHONPATH' environment variable may have.

    root_directory = os.path.dirname(__file__)
    boot_directory = os.path.join(root_directory, '__startup__')

    log_message('root_directory = %r', root_directory)
    log_message('boot_directory = %r', boot_directory)

    python_path = boot_directory

    if 'PYTHONPATH' in os.environ:
        path = os.environ['PYTHONPATH'].split(os.path.pathsep)
        if not boot_directory in path:
            python_path = "%s%s%s" % (boot_directory, os.path.pathsep,
                    os.environ['PYTHONPATH'])

    os.environ['PYTHONPATH'] = python_path

    # Set special environment variables which record the location of the
    # Python installation or virtual environment being used as well as
    # the Python version. The values of these are compared in the
    # 'sitecustomize' module with the values for the Python interpreter
    # which is later executed by the wrapper. If they don't match then
    # nothing will be done. This check is made as using the wrapper
    # script from one Python installation around 'python' executing from
    # a different installation can cause problems.

    os.environ['AUTOWRAPT_PYTHON_PREFIX'] = os.path.realpath(
            os.path.normpath(sys.prefix))
    os.environ['AUTOWRAPT_PYTHON_VERSION'] = '.'.join(
            map(str, sys.version_info[:2]))

    # Now launch the wrapped program. If the program to run was not an
    # absolute or relative path then we need to search the directories
    # specified in the 'PATH' environment variable to try and work out
    # where it is actually located.

    program_exe_path = args[0]

    if not os.path.dirname(program_exe_path):
        program_search_path = os.environ.get('PATH',
                '').split(os.path.pathsep)

        for path in program_search_path:
            path = os.path.join(path, program_exe_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                program_exe_path = path
                break

    log_message('program_exe_path = %r', program_exe_path)
    log_message('execl_arguments = %r', [program_exe_path]+args)

    os.execl(program_exe_path, *args)

def main():
    if len(sys.argv) <= 1:
        sys.exit('Usage: %s program [options]' % os.path.basename(
                sys.argv[0]))

    run_program(sys.argv[1:])

if __name__ == '__main__':
    main()
