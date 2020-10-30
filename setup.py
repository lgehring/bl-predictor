# This script tells python how to install our project and create
# redistributable package archives. It is best invoked indirectly
# through pip:
#
#   pip install -e .[dev]

# In the absence of parameters, this uses the values from `setup.cfg`:
from setuptools import setup
setup()
