from typing import Dict
from pathlib import Path
import logging

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

log = logging.getLogger(__name__)


def readconfig() -> Dict[str, str]:
    """Provides the current configuration

    Configuration is read from the [tool.micropython-stubber] section of 'pyproject.toml'.
    If not found defaults are used.

    - stub-folder
      - fallback-folder
    - repo-folder
      - mpy-folder
      - micropython-lib
    """
    config = {
        "stub-folder": "./stubs",
        # relative to stubs
        "fallback-folder": "typings/fallback",
        # ------------------------------
        "repo-folder": "./repos",
        # relative to repos
        "mpy-folder": "micropython",
        "mpy-lib-folder": "micropython-lib",
    }

    if Path("pyproject.toml").exists():
        try:
            with open("pyproject.toml", "rb") as f:
                toml_dict = tomllib.load(f)
        except tomllib.TOMLDecodeError:  # pragma: no cover
            log.warning("unable to read ")
        else:
            try:
                toml_config = toml_dict["tool"]["micropython-stubber"]
                config = {**config, **toml_config}

            except KeyError:  # pragma: no cover
                pass
    return config
