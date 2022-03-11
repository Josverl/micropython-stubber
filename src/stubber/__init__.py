"""read the version from pyproject or the wheels"""
try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

try:
    # todo: use __name__
    __version__ = importlib_metadata.version("micropython-stubber")
except Exception:
    __version__ = "0.0.0"

from . import utils

config = utils.readconfig()
