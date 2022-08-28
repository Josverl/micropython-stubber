from dataclasses import dataclass
from pathlib import Path


@dataclass
class FakeConfig:
    "Fake configuration to be used in testing" 
    ## 
    publish_path: Path = Path(".override/publish")
    stub_path: Path = Path(".override/repos/mpy-stubs/stubs")
    template_path: Path = Path(".override/publish/template")
    # below not yest used in testing
    repo_path: Path = Path(".override/repos")
    fallback_path: Path = Path(".override/fallback")
    mpy_path: Path = Path(".override/repos/mpy")
    mpy_lib_path: Path = Path(".override/repos/mpy-lib")
    mpy_stubs_repo_path: Path = Path(".override/repos/mpy-stubs")
