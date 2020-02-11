"""
Basic example for easy to create option-parsing.

Usage:
    scaffold [options] [<INPUT>...]

Options:
    -o FILE, --output FILE      Output file

    -v, --version               Show version information
    -h, --help                  Show this usage message
"""

from scaffold import __version__

from docopt import docopt


def main(args=None):
    opts = docopt(__doc__, args, version=__version__)
    print("Parsed options:", opts)
