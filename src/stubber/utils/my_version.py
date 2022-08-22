"""
find the version of this package
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata  # type: ignore

__version__ = "0.0.0"
try:
    # todo: use __name__
    __version__ = importlib_metadata.version("micropython-stubber")
except Exception:  # pragma: no cover
    __version__ = "0.0.0"
