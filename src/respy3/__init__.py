"""Respy3 is a protocol reader/writer for RESP3."""

from importlib import metadata

from .protocol import Resp3Reader, write_command

try:
    __version__ = metadata.version(__name__)
except Exception:  # pragma: no cover
    __version__ = "unknown"