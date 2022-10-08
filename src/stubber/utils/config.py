from pathlib import Path

from typedconfig.config import Config, key, section
from typedconfig.source import EnvironmentConfigSource

from .typed_config_toml import TomlConfigSource


@section("micropython-stubber")
class StubberConfig(Config):
    "stubber confguration class"
    stub_path = key(key_name="stub-path", cast=Path, required=False, default=Path("./stubs"))
    "a Path to the stubs directory"
    # relative to stubs folder
    fallback_path = key(key_name="fallback-path", cast=Path, required=False, default=Path("typings/fallback"))
    "a Path to the fallback stubs directory"

    # ------------------------------------------------------------------------------------------
    # micropython and micropython-lib are relative to ./repo folder
    repo_path = key(key_name="repo-path", cast=Path, required=False, default=Path("./repos"))
    "a Path to the repo directory"

    mpy_path = key(key_name="mpy-path", cast=Path, required=False, default=Path("micropython"))
    "a Path to the micropython folder in the repos directory"

    mpy_lib_path = key(key_name="mpy-lib-path", cast=Path, required=False, default=Path("micropython-lib"))
    "a Path to the micropython-lib folder in the repos directory"

    # mpy_stubs_repo_path = key(key_name="mpy-stubs-repo-path", cast=Path, required=False, default=Path("./micropython-stubs"))
    # "a Path to the micropython-stubs folder in the repos directory"

    publish_path = key(key_name="publish-path", cast=Path, required=False, default=Path("./repos/micropython-stubs/publish"))
    "a Path to the folder where all stub publication artefacts are stored"

    template_path = key(key_name="template-path", cast=Path, required=False, default=Path("./repos/micropython-stubs/publish/template"))
    "a Path to the publication folder that has the template files"

    def post_read_hook(self) -> dict:
        config_updates = dict()
        # relative to stubs
        config_updates.update(fallback_path=self.stub_path / self.fallback_path)

        # relative to repo path
        config_updates.update(mpy_path=self.repo_path / self.mpy_path)
        config_updates.update(mpy_lib_path=self.repo_path / self.mpy_lib_path)
        # config_updates.update(mpy_stubs_repo_path=self.repo_path / self.mpy_stubs_repo_path)
        return config_updates


def readconfig(filename: str = "pyproject.toml", prefix: str = "tool.", must_exist: bool = True):
    "read the configuration from the pyproject.toml file"
    # locate the pyproject.toml file
    path = Path.cwd()
    while not (path / filename).exists():
        path = path.parent
        if path == Path("/"):
            raise FileNotFoundError(f"Could not find config file {filename}")
    filename = str(path / filename)

    config = StubberConfig()
    # add provider sources to the config
    config.add_source(EnvironmentConfigSource())
    config.add_source(TomlConfigSource(filename, prefix=prefix, must_exist=must_exist))  # ,"tools.micropython-stubber"))
    config.read()
    return config


#######################
# config singleton
CONFIG = readconfig()
"stubber configuration singleton"
#######################
