"""
typed-config-toml

Extend typed-config to read configuration from .toml files

"""
# TODO : extend support for . notation in section names

from pathlib import Path
from typing import Dict, Optional

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib
assert tomllib

from loguru import logger as log
from typedconfig.source import ConfigSource


class TomlConfigSource(ConfigSource):
    """Read configuration from a .toml file

    prefix is used to allow for toml nested configuration
    a common prefix = "tool."

    ```
    #pyproject.toml
    [tool.deadparrot]
    species = "Norwegian Blue"
    state = "resting"
    details = ["pinging","Lovely plumage","3"]
    ```
    Use the below code to retrieve:
    ```
    # TODO sample code
    ```
    """

    def __init__(self, filename: str, prefix: Optional[str] = None, must_exist: bool = True):
        self.filename = filename
        toml_dict = {}
        if Path(self.filename).exists():
            # Read data - will raise an exception if problem with file
            try:
                with open(filename, "rb") as f:
                    toml_dict = tomllib.load(f)
            except tomllib.TOMLDecodeError:  # pragma: no cover
                log.warning("unable to read ")
        elif must_exist:
            raise FileNotFoundError(f"Could not find config file {self.filename}")
        if not prefix or len(prefix) == 0:
            self.data = toml_dict
        else:
            # common prefix = "tool."
            try:
                self.data = toml_dict[prefix.rstrip(".")]
            except KeyError:  # pragma: no cover
                self.data = {}

        # Quick checks on data format

        assert isinstance(self.data, Dict)
        for k, v in self.data.items():
            assert isinstance(k, str)
            assert isinstance(v, Dict)
            for v_k, v_v in v.items():  # type: ignore
                assert isinstance(v_k, str)
                # do not assume/require that all values are strings
                # assert isinstance(v_v, str)
        # Convert all keys to lowercase
        self.data = {k.lower(): {v_k.lower(): v_v for v_k, v_v in v.items()} for k, v in self.data.items()}

    def get_config_value(self, section_name: str, key_name: str) -> Optional[str]:
        # Extract info from data which we read in during __init__
        section = self.data.get(section_name.lower(), None)
        if section is None:
            return None
        return section.get(key_name.lower(), None)
