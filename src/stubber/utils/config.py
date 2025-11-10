"""stubber configuration"""

from pathlib import Path
from typing import List, Optional

from mpflash.logger import log
from mpflash.versions import (
    get_preview_mp_version,
    get_stable_mp_version,
    micropython_versions,
)
from typedconfig.config import Config, key, section
from typedconfig.source import EnvironmentConfigSource

from .typed_config_toml import TomlConfigSource

# Unified fallback version list used by both config.py and switch_cmd.py
# This list is used when GitHub API access fails (403 Forbidden)
FALLBACK_VERSIONS = [
    "1.17",
    "1.18",
    "1.19",
    "1.19.1",
    "1.20.0",
    "1.20.1",
    "1.21.0",
    "1.22.0",
    "1.22.1",
    "1.22.2",
    "1.23.0",
    "1.24.0",
    "1.25.0",
    "1.26.0",
]


@section("micropython-stubber")
class StubberConfig(Config):
    _config_path = None

    "stubber configuration class"
    # relative to stubs folder
    fallback_path: Path = key(
        key_name="fallback-path",
        cast=Path,
        required=False,
        default=Path("typings/fallback"),
    )
    "a Path to the fallback stubs directory"

    # ------------------------------------------------------------------------------------------
    # micropython and micropython-lib are relative to ./repo folder
    repo_path: Path = key(key_name="repo-path", cast=Path, required=False, default=Path("./repos"))
    "a Path to the repo directory"

    mpy_path: Path = key(key_name="mpy-path", cast=Path, required=False, default=Path("micropython"))
    "a Path to the micropython folder in the repos directory"

    mpy_lib_path: Path = key(
        key_name="mpy-lib-path",
        cast=Path,
        required=False,
        default=Path("micropython-lib"),
    )
    "a Path to the micropython-lib folder in the repos directory"

    mpy_stubs_path: Path = key(
        key_name="mpy-stubs-path",
        cast=Path,
        required=False,
        default=Path("micropython-stubs"),
    )
    "a Path to the micropython-stubs folder in the repos directory (or current directory)"

    typeshed_path: Path = key(
        key_name="typeshed-path",
        cast=Path,
        required=False,
        default=Path("typeshed"),
    )
    "a Path to the typeshed folder in the repos directory"

    stable_version: str = key(key_name="stable-version", cast=str, required=False, default="1.20.0")
    "last published stable"

    preview_version: str = key(key_name="preview-version", cast=str, required=False, default="preview")
    "current preview version"

    all_versions = key(
        key_name="all-versions",
        cast=list,
        required=False,
        default=FALLBACK_VERSIONS.copy(),
    )
    "list of recent versions"

    BLOCKED_PORTS = ["minimal", "bare-arm"]
    "ports that should be ignored as a source of stubs"

    @property
    def repos(self) -> List[Path]:
        "return the repo paths"
        return [self.mpy_path, self.mpy_lib_path, self.mpy_stubs_path, self.typeshed_path]

    @property
    def stub_path(self) -> Path:
        "return the stubs path in the microypthon-stubs repo"
        return self.mpy_stubs_path / "stubs"

    @property
    def publish_path(self) -> Path:
        "return the stubs path in the microypthon-stubs repo"
        return self.mpy_stubs_path / "publish"

    @property
    def template_path(self) -> Path:
        "return the stubs path in the microypthon-stubs repo"
        return self.mpy_stubs_path / "publish" / "template"

    @property
    def config_path(self) -> Path:
        "return the config path"
        return self._config_path

    @config_path.setter
    def config_path(self, value: Path):
        self._config_path = value

    def post_read_hook(self) -> dict:
        config_updates = {}
        # relative to stubs
        # config_updates.update(fallback_path=self.stub_path / self.fallback_path)

        # relative to repo path
        config_updates.update(mpy_path=self.repo_path / self.mpy_path)
        config_updates.update(mpy_lib_path=self.repo_path / self.mpy_lib_path)
        if self.mpy_stubs_path.is_absolute() or self.mpy_stubs_path == Path("."):
            config_updates.update(mpy_stubs_path=self.mpy_stubs_path)
        else:
            config_updates.update(mpy_stubs_path=self.repo_path / self.mpy_stubs_path)
        # read the versions from the git tags
        all_versions = []
        try:
            all_versions = micropython_versions(minver="v1.17")
        except Exception as e:
            log.warning(f"Could not read micropython versions from git: {e}")
            all_versions = FALLBACK_VERSIONS.copy()
        config_updates.update(all_versions=all_versions)
        # Try to get stable and preview versions, but use fallbacks if GitHub API fails
        try:
            stable_version = get_stable_mp_version()
            preview_version = get_preview_mp_version()
        except Exception as e:
            log.warning(f"Could not read stable/preview versions from git: {e}")
            stable_version = "1.20.0"  # fallback stable version
            preview_version = "preview"  # fallback preview version

        config_updates.update(
            stable_version=stable_version,
            preview_version=preview_version,
        )  # second last version - last version is the preview version
        return config_updates


def readconfig(
    location: Optional[Path] = None,
    filename: str = "pyproject.toml",
    prefix: str = "tool.",
    must_exist: bool = True,
):
    "read the configuration from the pyproject.toml file"
    # locate the pyproject.toml file
    config_path = location or Path.cwd()
    use_toml = True
    while not (config_path / filename).exists():
        config_path = config_path.parent
        if config_path == config_path.parent:
            log.trace(f"Could not find config file: {filename}")
            use_toml = False
            break

    filename = str(config_path / filename)

    config = StubberConfig()
    config.config_path = config_path.absolute()
    # add provider sources to the config
    config.add_source(EnvironmentConfigSource())
    if use_toml:
        config.add_source(TomlConfigSource(filename, prefix=prefix, must_exist=must_exist))  # ,"tools.micropython-stubber"))
    config.read()
    return config


#######################
# config singleton
CONFIG = readconfig()
"stubber configuration singleton"
#######################
