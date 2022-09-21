from dataclasses import InitVar, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FakeConfig:
    "Fake configuration to be used in testing"
    ##
    publish_path: Path = Path(".override/publish")
    stub_path: Path = Path(".override/repos/mpy-stubs/stubs")
    template_path: Path = Path(".override/publish/template")
    # init only variables
    tmp_path: InitVar[Path] = None  # type: ignore
    rootpath: InitVar[Path] = None  # type: ignore

    # below not yet used in testing
    repo_path: Path = Path(".override/repos")
    fallback_path: Path = Path(".override/fallback")
    mpy_path: Path = Path(".override/repos/mpy")
    mpy_lib_path: Path = Path(".override/repos/mpy-lib")
    mpy_stubs_repo_path: Path = Path(".override/repos/mpy-stubs")

    def __post_init__(self, tmp_path: Optional[Path] = None, rootpath: Optional[Path] = None):
        if tmp_path and rootpath:
            self.publish_path = tmp_path / "publish"
            self.stub_path = rootpath / "repos/micropython-stubs/stubs"
            self.template_path = rootpath / "tests/publish/data/template"

            self.publish_path.mkdir(parents=True)
