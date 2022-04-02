import logging
from pathlib import Path
from .typed_config_toml import EnvironmentConfigSource, TomlConfigSource, Config, key, section


log = logging.getLogger(__name__)


@section("micropython-stubber")
class StubberConfig(Config):
    "stubber confguration class"
    stub_path = key(key_name="stub-path", cast=Path, required=False, default=Path("./stubs"))
    "a Path to the stubs directory" 
    # relative to stubs folder
    fallback_path = key(key_name="fallback-path", cast=Path, required=False, default=Path("typings/fallback"))

    repo_path = key(key_name="repo-path", cast=Path, required=False, default=Path("./repo"))
    "a Path to the repo directory"
    # micropython and micropython-lib are relative to ./repo folder
    mpy_path = key(key_name="mpy-path", cast=Path, required=False, default=Path("micropython"))
    "a Path to the micropython dolder in the repo directory"
    mpy_lib_path = key(key_name="mpy-lib-path", cast=Path, required=False, default=Path("micropython-lib"))
    "a Path to the micropython=lib folder in the repo directory"

    def post_read_hook(self) -> dict:
        config_updates = dict()
        # relative to stubs
        config_updates.update(fallback_path=self.stub_path / self.fallback_path)

        # relative to repo path
        config_updates.update(mpy_path=self.repo_path / self.mpy_path)
        config_updates.update(mpy_lib_path=self.repo_path / self.mpy_lib_path)
        return config_updates


def readconfig():
    config = StubberConfig()
    config.add_source(EnvironmentConfigSource())
    config.add_source(TomlConfigSource("pyproject.toml", prefix="tool.", must_exist=False))  # ,"tools.micropython-stubber"))
    config.read()
    return config
