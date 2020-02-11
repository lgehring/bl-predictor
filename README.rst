Scaffold
--------
|Version| |License| |Python|

This serves as a skeleton for setting up new projects.

Usage
=====

To get started, follow these steps:

- Setup repository:

  - Create a new (empty) repository for your project on github.
  - ``git clone git@github.com:probabilistic-numerics/scaffold`` (clone the scaffold to your machine)
  - ``git remote set-url origin git@github.com:USERNAME/REPO`` (set up the remotes in your clone)
  - ``git push -u origin master`` (push initial version to your repository)

- Modify files:

  - Replace mentions of "scaffold" with your project name in every file
  - Remove unneeded files (e.g. cython example)
  - Fill in your code


Environment
===========

It is recommended to setup independent environments for every project. This
avoids version conflicts between different packages, makes it easier to keep
track of dependencies (type ``pip list`` to get a list of installed packages),
and may also improve performance (less packages on import path).

A good default tool for managing environments is *conda* (miniconda should
usually be perfectly suitable). After installation, conda makes creating and
activating python environments as easy as::

    conda create -n foobar python=3.7

    conda activate foobar

Once you've setup the environment, install the current package and its
dependencies with::

    pip install -e .[dev]

After making any changes to the cython module, the best way to recompile is::

    python setup.py build_ext --inplace

Other noteworthy tools for managing environments are

- virtualenvwrapper_ (more low-level, can only create environments for
  installed python versions)
- and Pipenv_ a more functional approach to package dependency management,
  specifically for applications, but in my opinion not yet mature enough

.. _miniconda:          https://docs.conda.io/en/latest/miniconda.html
.. _virtualenvwrapper:  https://virtualenvwrapper.readthedocs.io/
.. _Pipenv:             https://pipenv.kennethreitz.org/


Directory structure
===================

The following is a short overview of how to structure your python project::

    .
    ├── README.rst                          arguably the most important file
    ├── CHANGES.rst                         changelog, update between releases
    ├── COPYING.GPLv3.txt                   a reasonable starting license
    │
    ├── src
    │   └── scaffold
    │       ├── __init__.py                 toplevel package variables
    │       ├── __main__.py                 invoked on `python -m scaffold`
    │       ├── cli.py                      command line interface
    │       └── cython_example.pyx          cython is a C/python hybrid language
    │
    ├── docs
    │   ├── conf.py                         sphinx (doc builder) configuration
    │   ├── Makefile                        linux build script
    │   ├── make.bat                        windows build script
    │   └── index.rst                       source for site/index.html
    │
    ├── exp                                 experiments (e.g. jupyter notebooks)
    │   └── 00_sample.py                    example notebook
    │
    ├── tests
    │   ├── test_cli.py                     tests grouped by functionality
    │   └── test_cython_example.py
    │
    ├── setup.py                            packaging script
    ├── setup.cfg                           package metadata and tool configuration
    ├── pyproject.toml                      build system specification and tool config
    ├── MANIFEST.in                         list of files to be included in package
    ├── jupyter_notebook_config.py          used for commiting .py files instead of .ipynb
    ├── .gitignore                          list of files to be ignored by git
    ├── .appveyor.yml                       build scripts for Appveyor CI (windows)
    └── .travis.yml                         build scripts for Travis CI (linux)


Documentation
=============

If you want to recreate the documentation configuration from scratch, delete
everything in ``docs/`` and type::

    cd docs
    sphinx-quickstart

Then, commit the ``conf.py``, ``Makefile``, and ``.rst`` files.

To build the documentation locally, type::

    cd docs
    make html

    xdg-open _build/html/index.html


Tests
=====

|Appveyor| |Coverage|

We use flake8_ for basic syntax and style checks, and twine_ for checking the
created distributions.

Unit and integration tests are in the ``test/`` subdirectory and can be
executed via pytest_.

In order to trigger tests automatically on every push, you have to activate
your project on various continuous integration platforms:

- travis-ci.com_ for linux/mac testing
- appveyor.com_ for windows testing
- coveralls.io_ for coverage reports
- readthedocs.org_ documentation

.. _flake8:             https://flake8.pycqa.org/
.. _twine:              https://twine.readthedocs.io/
.. _pytest:             https://pytest.org/
.. _travis-ci.com:      https://travis-ci.com
.. _appveyor.com:       https://appveyor.com
.. _coveralls.io:       https://coveralls.io
.. _readthedocs.org:    https://readthedocs.org/


Packaging
=========

Before uploading a new version, first:

- update the version in ``src/<project>/__init__.py``
- compose a short changelog (``CHANGES.rst``)
- make sure that all tests are passing, and
- all dependencies are up to date

The basic procedure of creating a package and uploading it to PyPI_ looks as
follows::

    python setup.py sdist bdist_wheel
    twine check dist/*
    twine upload dist/*

However, this can be automated as well using the ``.travis.yml`` build
configuration. This happens in the *deploy* part, which is triggered whenever
a git *tag* is pushed to github, e.g.::

    git tag v1.0.2
    git push origin v1.0.2

For extra safety, you should consider first uploading test.pypi.org_ first.

.. _PyPI:               https://pypi.org/
.. _test.pypi.org:      https://test.pypi.org/


.. Badges:

.. |Version| image::    https://img.shields.io/pypi/v/scaffold.svg
   :target:             https://pypi.org/project/scaffold
   :alt:                Latest Version

.. |License| image::    https://img.shields.io/pypi/l/scaffold.svg
   :target:             https://github.com/probabilistic-numerics/scaffold/blob/master/COPYING.GPLv3.txt
   :alt:                License: CC0, Apache, Non-Free

.. |Python| image::     https://img.shields.io/pypi/pyversions/scaffold.svg
   :target:             https://pypi.org/project/scaffold#files
   :alt:                Python versions

.. |AppVeyor| image::   https://ci.appveyor.com/api/projects/status/github/probabilistic-numerics/scaffold?branch=master&svg=true
   :target:             https://ci.appveyor.com/project/coldfix/scaffold
   :alt:                Windows built status

.. |Travis| image::     https://api.travis-ci.org/probabilistic-numerics/scaffold.svg?branch=master
   :target:             https://travis-ci.org/probabilistic-numerics/scaffold
   :alt:                Linux build status

.. |Coverage| image::   https://coveralls.io/repos/probabilistic-numerics/scaffold/badge.svg?branch=master
   :target:             https://coveralls.io/r/probabilistic-numerics/scaffold
   :alt:                Coverage
