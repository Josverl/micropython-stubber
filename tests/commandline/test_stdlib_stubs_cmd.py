"""Tests for the stdlib command."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

import stubber.stubber as stubber

# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.cli]


##########################################################################################
# stdlib
##########################################################################################


@pytest.mark.mocked
def test_cmd_stdlib_stubs_help():
    """Test that the command shows help without errors."""
    runner = CliRunner()
    result = runner.invoke(stubber.stubber_cli, ["stdlib", "--help"])
    assert result.exit_code == 0
    assert "Build the micropython-stdlib-stubs package" in result.output


@pytest.mark.mocked
def test_cmd_stdlib_stubs_no_build(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command without building."""
    runner = CliRunner()

    # Mock get_stable_mp_version to return a fixed version
    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock Path operations and functions
    m_update_mpy_shed = mocker.patch("stubber.commands.stdlib_stubs_cmd.update_mpy_shed")
    m_update_asyncio = mocker.patch("stubber.commands.stdlib_stubs_cmd.update_asyncio_manual")
    m_post_processing = mocker.patch("stubber.commands.stdlib_stubs_cmd.do_post_processing")
    m_add_type_ignore = mocker.patch("stubber.commands.stdlib_stubs_cmd.add_type_ignore")
    m_comment_out = mocker.patch("stubber.commands.stdlib_stubs_cmd.comment_out_lines")
    m_change_lines = mocker.patch("stubber.commands.stdlib_stubs_cmd.change_lines")
    m_update_typing = mocker.patch("stubber.commands.stdlib_stubs_cmd.update_typing_pyi")

    # Mock CONFIG by creating a fake config object
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directory structure
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run command without building
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--no-merge", "--no-typeshed"],
    )

    # Command should succeed
    assert result.exit_code == 0

    # Verify the expected functions were called
    assert m_update_mpy_shed.call_count == 1
    assert m_update_asyncio.call_count == 1
    assert m_post_processing.call_count == 1
    assert m_add_type_ignore.call_count == 1
    assert m_comment_out.call_count == 1
    assert m_change_lines.call_count == 1
    assert m_update_typing.call_count == 1


@pytest.mark.mocked
def test_cmd_stdlib_stubs_with_merge(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with merge option."""
    runner = CliRunner()

    # Mock version function
    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock merge function
    m_merge = mocker.patch("stubber.commands.stdlib_stubs_cmd.merge_docstubs_into_stdlib")

    # Mock other functions
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_mpy_shed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_asyncio_manual")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.do_post_processing")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.add_type_ignore")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.comment_out_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.change_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_typing_pyi")

    # Mock CONFIG
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    docstubs_path = tmp_path / "stubs" / "micropython-v1_24_0-docstubs"
    docstubs_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run with merge
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--merge", "--no-typeshed"],
    )

    # Should succeed
    assert result.exit_code == 0

    # Verify merge was called
    assert m_merge.call_count == 1


@pytest.mark.mocked
def test_cmd_stdlib_stubs_with_typeshed(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with typeshed update."""
    runner = CliRunner()

    # Mock version
    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock typeshed update
    m_update_typeshed = mocker.patch("stubber.commands.stdlib_stubs_cmd.update_stdlib_from_typeshed")

    # Mock other functions
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_mpy_shed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_asyncio_manual")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.do_post_processing")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.add_type_ignore")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.comment_out_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.change_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_typing_pyi")

    # Mock CONFIG
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    typeshed_path = tmp_path / "repos" / "typeshed"
    typeshed_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run with typeshed update
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--no-merge", "--typeshed"],
    )

    # Should succeed
    assert result.exit_code == 0

    # Verify typeshed update was called
    assert m_update_typeshed.call_count == 1


@pytest.mark.mocked
def test_cmd_stdlib_stubs_version_option(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with explicit version."""
    runner = CliRunner()

    # Don't mock get_stable_mp_version since we're providing version explicitly
    m_version = mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock other functions
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_mpy_shed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_asyncio_manual")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.do_post_processing")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.add_type_ignore")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.comment_out_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.change_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_typing_pyi")

    # Mock CONFIG
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run with explicit version
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--no-merge", "--no-typeshed", "-v", "1.23.0"],
    )

    # Should succeed without calling get_stable_mp_version
    assert result.exit_code == 0
    assert m_version.call_count == 0


@pytest.mark.mocked
def test_cmd_stdlib_clone(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with clone option."""
    runner = CliRunner()

    # Mock version
    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock git operations
    m_git_clone = mocker.patch("stubber.commands.stdlib_stubs_cmd.git.clone")
    m_git_fetch = mocker.patch("stubber.commands.stdlib_stubs_cmd.git.fetch")
    m_git_pull = mocker.patch("stubber.commands.stdlib_stubs_cmd.git.pull")

    # Mock other functions
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_mpy_shed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_asyncio_manual")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.do_post_processing")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.add_type_ignore")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.comment_out_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.change_lines")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.update_typing_pyi")

    # Mock CONFIG
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run with clone (typeshed doesn't exist yet)
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--no-merge", "--no-typeshed", "--clone"],
    )

    # Should succeed
    assert result.exit_code == 0

    # Verify git.clone was called
    assert m_git_clone.call_count == 1
    assert m_git_fetch.call_count == 0
    assert m_git_pull.call_count == 0
