import os
from pathlib import Path

import pytest

from stubber.utils.config import StubberConfig, TomlConfigSource, readconfig

pytestmark = [pytest.mark.stubber]


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

    assert config.repo_path == Path("./my-repos")
    assert config.mpy_path == Path("./my-repos/micropython")
    assert config.mpy_lib_path == Path("./my-repos/micropython-lib")
    assert config.mpy_stubs_path == Path("./my-repos/micropython-stubs")
    # TODO Make sure this is relative to the stubs repo
    assert config.stub_path == Path("./my-repos/micropython-stubs/stubs")
    assert config.publish_path == Path("./my-repos/micropython-stubs/publish")


def test_config_stubs_repo():
    # test config used in the stubs repo
    config = readconfig(filename="tests/data/stubs_repo.toml", prefix="tool.", must_exist=True)
    assert config.repo_path == Path("./repos")
    assert config.mpy_path == Path("./repos/micropython")
    assert config.mpy_lib_path == Path("./repos/micropython-lib")

    assert config.mpy_stubs_path == Path(".")
    assert config.stub_path == Path("./stubs")
    assert config.publish_path == Path("./publish")


@pytest.fixture
def change_test_dir(request):
    """Change the working directory to the test directory, and back after the test."""
    os.chdir(request.fspath.dirname)
    try:
        yield
    finally:
        os.chdir(request.config.invocation_params.dir)


def test_config_no_config(change_test_dir, tmp_path: Path):
    # there will be no config file in the test directory
    os.chdir(tmp_path)
    config = readconfig()
    assert config.repo_path == Path("./repos")
    assert config.mpy_path == Path("./repos/micropython")
    assert config.mpy_lib_path == Path("./repos/micropython-lib")
    assert config.mpy_stubs_path == Path("./repos/micropython-stubs")

    assert config.publish_path == Path("./repos/micropython-stubs/publish")
