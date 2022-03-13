from importlib.resources import path
from typing import Any, Dict, Union
from pathlib import Path

# from typedconfig.config import Config, key, section
# from typedconfig.source import ConfigSource, EnvironmentConfigSource

from .typed_config_toml import EnvironmentConfigSource, TomlConfigSource, Config, key, section

import logging

log = logging.getLogger(__name__)


@section("micropython-stubber")
class StubberConfig(Config):
    "stubber confguration class"
    stub_path = key(key_name="stub-path", cast=Path, required=False, default=Path("./stubs"))
    # relative to stub
    fallback_path = key(key_name="fallback-path", cast=Path, required=False, default=Path("typings/fallback"))

    repo_path = key(key_name="repo-path", cast=Path, required=False, default=Path("./repo"))
    # relative to repo
    mpy_path = key(key_name="mpy-path", cast=Path, required=False, default=Path("./micropython"))
    mpy_lib_path = key(key_name="mpy-lib-path", cast=Path, required=False, default=Path("./micropython-lib"))

    def post_read_hook(self) -> dict:
        config_updates = dict()
        # relative to repo path
        config_updates.update(mpy_path=self.repo_path / self.mpy_path)
        config_updates.update(mpy_lib_path=self.repo_path / self.mpy_lib_path)

        # relative to stubs
        config_updates.update(fallback_path=self.stub_path / self.fallback_path)

        return config_updates

    # fallback_path = stub_path / str(_fallback_folder)

    # stub_folder = key(key_name="stub-folder", cast=str, required=False, default="./stubs")
    # stub_path = Path(str(stub_folder))

    # repo_folder = key(key_name="repo-folder", cast=str, required=False, default="./repo")
    # repo_path = Path(str(repo_folder))
    # mpy_folder = key(key_name="mpy-folder", cast=str, required=False, default="micropython")
    # mpy_lib_folder = key(key_name="mpy-lib-folder", cast=str, required=False, default="micropython-lib")
    # mpy_path = repo_path / str(mpy_folder)
    # mpy_lib_path = repo_path / str(mpy_lib_folder)


def readconfig():
    config = StubberConfig()
    config.add_source(EnvironmentConfigSource())
    config.add_source(TomlConfigSource("pyproject.toml", prefix="tool.", must_exist=False))  # ,"tools.micropython-stubber"))
    config.read()
    return config


# try:
#     import tomllib  # type: ignore
# except ModuleNotFoundError:
#     import tomli as tomllib

# def readconfig2() -> Dict[str, Union[str, Path]]:
#     """Provides the current configuration

#     Configuration is read from the [tool.micropython-stubber] section of 'pyproject.toml'.
#     If not found defaults are used.

#     - stub-folder
#       - fallback-folder
#     - repo-folder
#       - mpy-folder
#       - micropython-lib
#     """
#     config: Dict[str, Union[str, Path]] = {
#         "stub-folder": "./stubs",
#         # relative to stubs
#         "fallback-folder": "typings/fallback",
#         # ------------------------------
#         "repo-folder": "./repos",
#         # relative to repos
#         "mpy-folder": "micropython",
#         "mpy-lib-folder": "micropython-lib",
#     }

#     if Path("pyproject.toml").exists():
#         try:
#             with open("pyproject.toml", "rb") as f:
#                 toml_dict = tomllib.load(f)
#         except tomllib.TOMLDecodeError:  # pragma: no cover
#             log.warning("unable to read ")
#         else:
#             try:
#                 toml_config = toml_dict["tool"]["micropython-stubber"]
#                 config = {**config, **toml_config}

#             except KeyError:  # pragma: no cover
#                 pass
#     # Add common paths
#     config["lib-path"] = Path(config["lib-folder"])
#     config["repo-path"] = Path(config.repo_path.as_posix())
#     config["mpy-path"] = Path(config.repo_path.as_posix()) / config["mpy-folder"]
#     config["mpy-lib-path"] = Path(config.repo_path.as_posix()) / config["mpy-lib-folder"]

#     return config
