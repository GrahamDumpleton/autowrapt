import sys
import os

from setuptools import setup
from distutils.sysconfig import get_python_lib

setup_kwargs = dict(
    name = 'autowrapt',
    version = '1.0',
    description = 'Boostrap mechanism for monkey patches.',
    author = 'Graham Dumpleton',
    author_email = 'Graham.Dumpleton@gmail.com',
    license = 'BSD',
    url = 'https://github.com/GrahamDumpleton/autowrapt',
    packages = ['autowrapt'],
    package_dir = {'autowrapt': 'src'},
    data_files = [(get_python_lib(prefix=''), ['autowrapt-init.pth'])],
    entry_points = {'autowrapt.examples':
            ['this = autowrapt.examples:autowrapt_this']},
    install_requires = ['wrapt>=1.10.4'],
)

setup(**setup_kwargs)
