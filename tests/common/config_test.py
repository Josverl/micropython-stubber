from typing import Dict
from pathlib import Path

import pytest
import stubber
from stubber.utils.config import StubberConfig, TomlConfigSource, readconfig


def test_toplevel_config():
    # exists on top-level
    assert stubber.config
    assert isinstance(stubber.config, StubberConfig)

    assert isinstance(stubber.config.stub_path, Path)
    assert isinstance(stubber.config.repo_path, Path)
    # assert isinstance(stubber.config.fallback_path, Path )
    # assert isinstance(stubber.config.mpy_path, Path )
    # assert isinstance(stubber.config.mpy_lib_path, Path )


def test_bad_config_source():
    # throws error if file not found
    with pytest.raises(FileNotFoundError) as exc_info:
        source = TomlConfigSource("test/data/no_config.toml", must_exist=True)
    exception_raised = exc_info.value
    assert exception_raised.args[0] == "Could not find config file test/data/no_config.toml"


def test_ok_config_source():
    source = TomlConfigSource("tests/data/test.toml", must_exist=True)
    assert isinstance(source, TomlConfigSource)


def test_ok_config_source_prefix():
    source = TomlConfigSource("tests/data/test.toml", prefix=".tool", must_exist=True)
    assert isinstance(source, TomlConfigSource)


def test_config():
    config = readconfig(filename="tests/data/test.toml", prefix="tool.", must_exist=True)

    assert isinstance(config, StubberConfig)
    assert isinstance(config.stub_path, Path)
    assert isinstance(config.repo_path, Path)
    assert isinstance(config.fallback_path, Path)
    assert isinstance(config.mpy_path, Path)
    assert isinstance(config.mpy_lib_path, Path)

    assert config.stub_path == Path("./my-stubs")
