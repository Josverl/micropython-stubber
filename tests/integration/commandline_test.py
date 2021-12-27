import pytest
from pathlib import Path
from click.testing import CliRunner

# module under test :
from get_all_frozen import get_all


def test_get_all_help():
    # check basic commandline sanity check
    runner = CliRunner()
    result = runner.invoke(get_all, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--all" in result.output
    assert "Get all frozen modules" in result.output


@pytest.mark.slow
def test_get_all_lobo(tmp_path: Path):
    # check basic commandline for lobo download
    runner = CliRunner()
    result = runner.invoke(get_all, ["-stubs", tmp_path.as_posix(), "--lobo"])
    assert result.exit_code == 0
    assert "Downloading writer.py" in result.output
    assert "running stubgen" in result.output
    assert result.exception == None


@pytest.mark.slow
def test_get_all_core(tmp_path: Path):
    # check basic commandline test
    runner = CliRunner()
    result = runner.invoke(get_all, ["-stubs", tmp_path.as_posix(), "--core", "--no-pyi"])
    assert result.exit_code == 0
    assert result.exception == None


@pytest.mark.slow
def test_get_all_mpy(tmp_path: Path):
    # check basic commandline test
    runner = CliRunner()
    result = runner.invoke(get_all, ["-stubs", tmp_path.as_posix(), "--mpy", "--no-pyi"])
    assert result.exit_code == 0
    assert result.exception == None
