import sys
import os

from distutils.core import setup
from distutils.sysconfig import get_python_lib

ENTRY_POINTS = [
    'this = autowrapt_demos:autowrapt_this',
]

setup_kwargs = dict(
    name = 'autowrapt',
    version = '1.0',
    description = 'Boostrap mechanism for monkey patches.',
    author = 'Graham Dumpleton',
    author_email = 'Graham.Dumpleton@gmail.com',
    license = 'BSD',
    url = 'https://github.com/GrahamDumpleton/autowrapt',
    py_modules = ['autowrapt', 'autowrapt_demos'],
    data_files = [(get_python_lib(prefix=''), ['autowrapt-init.pth'])],
    entry_points = {'autowrapt_demos': ENTRY_POINTS},
    install_requires = ['wrapt>=1.10.4'],
)

setup(**setup_kwargs)
