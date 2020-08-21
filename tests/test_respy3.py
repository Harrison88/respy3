"""Test the version number is set."""

from importlib import metadata

from respy3 import __version__


def test_version():
    """It has the correct __version__."""
    assert __version__ == metadata.version("respy3")
