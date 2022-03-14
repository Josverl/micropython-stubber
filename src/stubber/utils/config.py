import logging
from pathlib import Path
from .typed_config_toml import EnvironmentConfigSource, TomlConfigSource, Config, key, section


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


def readconfig():
    config = StubberConfig()
    config.add_source(EnvironmentConfigSource())
    config.add_source(TomlConfigSource("pyproject.toml", prefix="tool.", must_exist=False))  # ,"tools.micropython-stubber"))
    config.read()
    return config
