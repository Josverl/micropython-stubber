"""
Classes and functions copied & adapted from micropypythons makemanifest.py to ensure that the manifest.py files can be processed
"""
import os
import shutil
from pathlib import Path
from typing import List, Union

from loguru import logger as log

# # log = logging.getLogger(__name__)
# log.setLevel(level=logging.DEBUG)

path_vars = {"MPY_DIR": "", "MPY_LIB_DIR": "", "PORT_DIR": "", "BOARD_DIR": ""}

# do not change class name
class FreezeError(Exception):
    pass


# do not change class name
class IncludeOptions:  # pragma: no cover
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._defaults = {}

    def defaults(self, **kwargs):
        self._defaults = kwargs

    def __getattr__(self, name):
        return self._kwargs.get(name, self._defaults.get(name, None))


# do not change method name
# freeze_as_mpy is only used by the unix port.
def freeze_as_mpy(path, script=None, opt=0):
    log.trace(" - freeze_as_mpy({},script={},opt={})".format(path, script, opt))
    freeze(path, script, opt)


# do not change method name
def freeze_as_str(path):  # pragma: no cover
    log.trace(" - freeze_as_str({})".format(path))
    freeze(path)


# do not change method name
def freeze_mpy(path, script=None, opt=0):  # pragma: no cover
    """Freeze the input (see above), which must be .mpy files that are
    frozen directly.
    """
    log.trace(" - freeze_as_mpy({})".format(path))
    freeze(path, script)


# function used commonly in manifest.py to freeze a set of scripts
# pylint: disable=unused-argument, unused-variable
# do not change method name
def freeze(path, script=None, opt=0):  # pragma: no cover
    """Freeze the input, automatically determining its type.  A .py script
    will be compiled to a .mpy first then frozen, and a .mpy file will be
    frozen directly.

    `path` must be a directory, which is the base directory to search for
    files from.  When importing the resulting frozen modules, the name of
    the module will start after `path`, ie `path` is excluded from the
    module name.

    If `path` is relative, it is resolved to the current manifest.py.
    Use $(MPY_DIR), $(MPY_LIB_DIR), $(PORT_DIR), $(BOARD_DIR) if you need
    to access specific paths.

    If `script` is None all files in `path` will be frozen.

    If `script` is an iterable then freeze() is called on all items of the
    iterable (with the same `path` and `opt` passed through).

    If `script` is a string then it specifies the filename to freeze, and
    can include extra directories before the file.  The file will be
    searched for in `path`.

    `opt` is the optimisation level to pass to mpy-cross when compiling .py
    to .mpy. (ignored in this implementation)
    """
    log.trace(" - freeze(({},script={},opt={})".format(path, script, opt))
    path = convert_path(path)
    if script is None:
        # folder of scripts.
        # for s in os.listdir(path):
        #     freeze_internal(path, s)

        for dirpath, dirnames, filenames in os.walk(path, followlinks=True):  # type: ignore
            for script in filenames:
                # can recurse folder, so add relative path to script.
                freeze_internal(path, (dirpath + "/" + script)[len(path) + 1 :], opt)
    elif not isinstance(script, str):
        # several specific scripts.
        for script in script:
            freeze_internal(path, script)
    else:
        # on specific script, may include a path: 'umqtt/simple.py'
        freeze_internal(path, script)


# do not change method name
def include(manifest: Union[str, List[str]], **kwargs):
    """
    Include another manifest.

    The manifest argument can be a string (filename) or an iterable of
    strings.

    Relative paths are resolved with respect to the current manifest file.

    Optional kwargs can be provided which will be available to the
    included script via the `options` variable.

    e.g. include("path.py", extra_features=True)

    in path.py:
        options.defaults(standard_features=True)

        # freeze minimal modules.
        if options.standard_features:
            # freeze standard modules.
        if options.extra_features:
            # freeze extra modules.
    """
    if not isinstance(manifest, Path) and not isinstance(manifest, str):  # type: ignore
        for m in manifest:
            include(m)
    else:
        manifest = convert_path(manifest)
        with open(manifest) as f:
            # Make paths relative to this manifest file while processing it.
            # Applies to includes and input files.
            prev_cwd = os.getcwd()
            os.chdir(os.path.dirname(manifest))
            try:
                # exec(f.read())  # pylint: disable=exec-used
                exec(f.read(), globals(), {"options": IncludeOptions(**kwargs)})  # pylint: disable=exec-used
            except OSError:
                log.warning("Could not process manifest: {}".format(manifest))
            os.chdir(prev_cwd)


# path_vars MUST be set externally
def convert_path(path: str) -> str:
    "Perform variable substitution in path"
    for name, value in path_vars.items():
        path = path.replace("$({})".format(name), value)
    # Convert to absolute path (so that future operations don't rely on
    # still being chdir 'ed).
    return os.path.abspath(path)


# -------------------------------------------------------------------------
# plug in the microsoft-stubber functionality
#

# stubdir MUST be set externally
stub_dir: str = ""
from pathlib import Path


# called by freeze.
# do not change method name
def freeze_internal(path: str, script: str, opt=None):
    """
    Copy the to-be-frozen module to the destination folder to be stubbed.

    Parameters:
    path (str)  : the source path
    script (str): the source script to be frozen
    opt (Any): freeze option (ignored)
    """

    log.trace(f" - freeze_internal({path},{script})")

    _path = Path(convert_path(path))
    source_path = _path / script
    dest_path = Path(stub_dir) / script

    if not _path.is_dir():  # pragma: no cover
        raise FreezeError("freeze source path should be a directory")
    if not stub_dir or stub_dir == "":  # pragma: no cover
        raise FreezeError("Stub folder not set")

    log.debug(f"freeze_internal : {script:<30} to {stub_dir}")
    # ensure folder, including possible path prefix for script
    os.makedirs(dest_path.parent, exist_ok=True)
    # copy file
    try:
        shutil.copy2(source_path, dest_path)
    except (FileNotFoundError) as e:  # pragma: no cover
        log.warning(f"File {path}/{script} not found")
    except (OSError, FileNotFoundError) as e:  # pragma: no cover
        log.exception(e)
