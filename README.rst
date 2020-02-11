Teamproject
-----------

This serves as a skeleton for setting up new projects.

Usage
=====

To get started, follow these steps:

- Fork this repository to your project on github.
- clone the project to your machine, e.g. ``git clone git@github.com:<USERNAME>/swp-teamproject``
- Replace mentions of "teamproject" with your project name in every file


Environment
===========

It is recommended to setup independent environments for every project. This
avoids version conflicts between different packages, makes it easier to keep
track of dependencies (type ``pip list`` to get a list of installed packages),
and may also improve performance (less packages on import path).

A good default tool for managing environments is *conda* (miniconda_ should
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
    │
    ├── teamproject
    │   ├── __init__.py                     toplevel package variables
    │   ├── __main__.py                     invoked on `python -m teamproject`
    │   ├── crawler.py                      web-crawler / queries
    │   ├── gui.py                          defines the gui code
    │   └── models                          ML code for predictions
    │       └── nonsense.py                 nonsensical example
    │
    ├── tests
    │   ├── test_crawler.py                 tests grouped by functionality
    │   ├── test_gui.py
    │   └── test_model_nonsense.py
    │
    ├── setup.py                            packaging script
    ├── setup.cfg                           package metadata and tool configuration
    ├── MANIFEST.in                         list of files to be included in package
    ├── .gitignore                          list of files to be ignored by git
    ├── .appveyor.yml                       build scripts for Appveyor CI (windows)
    └── .travis.yml                         build scripts for Travis CI (linux)


Tests
=====

We use flake8_ for basic syntax and style checks, and twine_ for checking the
created distributions.

Unit and integration tests are in the ``test/`` subdirectory and can be
executed via pytest_.

In order to trigger tests automatically on every push, you have to activate
your project on one or more continuous integration platforms:

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
