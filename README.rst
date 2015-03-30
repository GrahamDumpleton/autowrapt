=========
autowrapt
=========

A Python module for triggering monkey patching of a Python application,
without the need to actually modify the Python application itself to
setup the monkey patches.

The package works in conjunction with the ``wrapt`` module. One would
create post import hook patch modules per ``wrapt`` module requirements,
and then list the names of the setuptools entrypoints you wish to enable in
the ``AUTOWRAPT_BOOTSTRAP`` environment variable, when executing Python
within the environment that the ``autowrapt`` module is installed.
