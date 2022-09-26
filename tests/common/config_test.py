from pathlib import Path

import pytest
from stubber.utils.config import StubberConfig, TomlConfigSource, readconfig


def test_toplevel_config():
    # exists on top-level
    from stubber.utils.config import CONFIG

    assert CONFIG
    assert isinstance(CONFIG, StubberConfig)

    assert isinstance(CONFIG.stub_path, Path)
    assert isinstance(CONFIG.repo_path, Path)
    assert isinstance(CONFIG.fallback_path, Path)
    assert isinstance(CONFIG.mpy_path, Path)
    assert isinstance(CONFIG.mpy_lib_path, Path)


def test_bad_config_source():
    # throws error if file not found
    with pytest.raises(FileNotFoundError) as exc_info:
        _ = TomlConfigSource("test/data/no_config.toml", must_exist=True)
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
    assert config.repo_path == Path("./my-repos")
    assert config.mpy_path == Path("./my-repos/micropython")
    # TODO Make sure this is relative to the stubs repo
    assert config.publish_path == Path("./repos/micropython-stubs/publish")
