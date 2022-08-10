from typing import Dict
from pathlib import Path

import pytest
import stubber
from stubber.utils.config import StubberConfig, TomlConfigSource


def test_toplevel_config():
    # exists on top-level
    assert stubber.config
    assert isinstance(stubber.config, StubberConfig)

    print(stubber.config)
    assert isinstance(stubber.config.stub_path, Path)
    assert isinstance(stubber.config.repo_path, Path)
    # assert isinstance(stubber.config.fallback_path, Path )
    # assert isinstance(stubber.config.mpy_path, Path )
    # assert isinstance(stubber.config.mpy_lib_path, Path )


@pytest.mark.skip(reason="TODO: test incomplete")
def test_config_from_pyproject_toml():
    # test if the config reads from the pyproject.toml file

    config = StubberConfig()
    assert isinstance(config, StubberConfig)

    config.add_source(TomlConfigSource("pyproject.toml", prefix="tool.", must_exist=False))
    assert isinstance(config, StubberConfig)
