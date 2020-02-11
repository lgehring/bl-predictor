# encoding: utf-8
"""
Setup script.

Usage:
    python setup.py sdist bdist_wheel

This script is meant for creating the distributable package archives.
Developers who wish to install this package locally should run instead:

    pip install -e .[dev]
"""

# uses metadata from `setup.cfg`:
from setuptools import setup
setup()
