# encoding: utf-8
"""
Setup script.

Usage:
    python setup.py sdist bdist_wheel

This script is meant for creating the distributable package archives.
Developers who wish to install this package locally should run instead:

    pip install -e .[dev]
"""

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

extension_args = {
    'libraries': [],
    'extra_compile_args': [],
    'extra_link_args': [],
}

# Further metadata is defined in `setup.cfg`!
setup(
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=cythonize([
        Extension(
            'scaffold.cython_example',
            sources=['src/scaffold/cython_example.pyx'],
            **extension_args)
    ]),
)
