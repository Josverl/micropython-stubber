from typing import Dict
from pathlib import Path
import logging

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

log = logging.getLogger(__name__)


def readconfig() -> Dict[str, str]:
    config = {
        "stub-folder": "./stubs",
        "repo-folder": "repos",
        "mpy-folder": "micropython",
        "mpy-lib-folder": "micropython-lib",
    }

    if Path("pyproject.toml").exists():
        try:
            with open("pyproject.toml", "rb") as f:
                toml_dict = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            log.warning("unable to read ")
        else:
            try:
                toml_config = toml_dict["tool"]["micropython-stubber"]
                config = {**config, **toml_config}

            except KeyError:
                pass
    return config
