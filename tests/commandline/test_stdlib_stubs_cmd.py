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
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
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
        ["stdlib", "--no-build", "--no-merge", "--no-update"],
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
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
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
        ["stdlib", "--no-build", "--merge", "--no-update"],
    )

    # Should succeed
    assert result.exit_code == 0

    # Verify merge was called
    assert m_merge.call_count == 1


@pytest.mark.mocked
def test_cmd_stdlib_stubs_with_update(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with update option."""
    runner = CliRunner()

    # Mock version
    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.get_stable_mp_version",
        return_value="1.24.0",
    )

    # Mock update function
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
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
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

    # Run with update option
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--no-build", "--no-merge", "--update"],
    )

    # Should succeed
    assert result.exit_code == 0

    # Verify update was called
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
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
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
        ["stdlib", "--no-build", "--no-merge", "--no-update", "-v", "1.23.0"],
    )

    # Should succeed without calling get_stable_mp_version
    assert result.exit_code == 0
    assert m_version.call_count == 0


##########################################################################################
# Unit tests for helper functions
##########################################################################################


def test_extract_error_lines():
    """Test _extract_error_lines function."""
    from stubber.commands.stdlib_stubs_cmd import _extract_error_lines

    # Test with short text
    text = "Error line 1\nError line 2\nError line 3"
    result = _extract_error_lines(text)
    assert result == "Error line 1\nError line 2\nError line 3"

    # Test with long text (more than max_lines)
    text = "\n".join([f"Line {i}" for i in range(20)])
    result = _extract_error_lines(text, max_lines=5)
    assert result == "Line 15\nLine 16\nLine 17\nLine 18\nLine 19"

    # Test with empty lines
    text = "Line 1\n\n\nLine 2\n\nLine 3"
    result = _extract_error_lines(text)
    assert result == "Line 1\nLine 2\nLine 3"


def test_update_stdlib_from_typeshed(tmp_path: Path):
    """Test update_stdlib_from_typeshed function."""
    from stubber.commands.stdlib_stubs_cmd import update_stdlib_from_typeshed

    # Create mock typeshed structure
    typeshed_path = tmp_path / "typeshed"
    typeshed_stdlib = typeshed_path / "stdlib"
    typeshed_stdlib.mkdir(parents=True)

    # Create a module file
    (typeshed_stdlib / "sys.pyi").write_text("# sys module")

    # Create a package directory
    asyncio_dir = typeshed_stdlib / "asyncio"
    asyncio_dir.mkdir()
    (asyncio_dir / "__init__.pyi").write_text("# asyncio package")

    # Create dist path
    dist_stdlib_path = tmp_path / "dist"
    dist_stdlib_path.mkdir()

    # Run the function
    update_stdlib_from_typeshed(dist_stdlib_path, typeshed_path)

    # Verify files were copied
    stdlib_path = dist_stdlib_path / "stdlib"
    assert stdlib_path.exists()
    assert (stdlib_path / "sys.pyi").exists()
    assert (stdlib_path / "asyncio" / "__init__.pyi").exists()


def test_update_stdlib_from_typeshed_missing_path(tmp_path: Path):
    """Test update_stdlib_from_typeshed with missing typeshed path."""
    from stubber.commands.stdlib_stubs_cmd import update_stdlib_from_typeshed

    typeshed_path = tmp_path / "nonexistent"
    dist_stdlib_path = tmp_path / "dist"
    dist_stdlib_path.mkdir()

    with pytest.raises(FileNotFoundError):
        update_stdlib_from_typeshed(dist_stdlib_path, typeshed_path)


def test_update_mpy_shed(tmp_path: Path):
    """Test update_mpy_shed function."""
    from stubber.commands.stdlib_stubs_cmd import update_mpy_shed

    # Create mock reference structure
    reference_path = tmp_path / "reference"
    mpy_shed_src = reference_path / "_mpy_shed"
    mpy_shed_src.mkdir(parents=True)
    (mpy_shed_src / "test.pyi").write_text("# test")

    # Create dist path
    dist_stdlib_path = tmp_path / "dist"
    dist_stdlib_path.mkdir()

    # Run the function
    update_mpy_shed(reference_path, dist_stdlib_path)

    # Verify files were copied
    mpy_shed_dst = dist_stdlib_path / "stdlib" / "_mpy_shed"
    assert mpy_shed_dst.exists()
    assert (mpy_shed_dst / "test.pyi").exists()


def test_update_asyncio_manual(tmp_path: Path):
    """Test update_asyncio_manual function."""
    from stubber.commands.stdlib_stubs_cmd import update_asyncio_manual

    # Create mock reference structure
    reference_path = tmp_path / "reference"
    asyncio_src = reference_path / "asyncio"
    asyncio_src.mkdir(parents=True)
    (asyncio_src / "__init__.pyi").write_text("# asyncio")

    # Create dist path
    dist_stdlib_path = tmp_path / "dist"
    dist_stdlib_path.mkdir()

    # Run the function
    update_asyncio_manual(reference_path, dist_stdlib_path)

    # Verify files were copied
    asyncio_dst = dist_stdlib_path / "stdlib" / "asyncio"
    assert asyncio_dst.exists()
    assert (asyncio_dst / "__init__.pyi").exists()


def test_merge_docstubs_into_stdlib(tmp_path: Path, mocker: MockerFixture):
    """Test merge_docstubs_into_stdlib function."""
    from stubber.commands.stdlib_stubs_cmd import merge_docstubs_into_stdlib

    # Create mock paths
    dist_stdlib_path = tmp_path / "dist"
    stdlib_path = dist_stdlib_path / "stdlib"
    stdlib_path.mkdir(parents=True)

    docstubs_path = tmp_path / "docstubs"
    docstubs_path.mkdir()

    boardstub_path = tmp_path / "boardstubs"
    boardstub_path.mkdir()

    # Mock enrich_folder
    m_enrich = mocker.patch("stubber.commands.stdlib_stubs_cmd.enrich_folder", return_value=5)

    # Run the function
    merge_docstubs_into_stdlib(dist_stdlib_path, docstubs_path, boardstub_path)

    # Verify enrich_folder was called twice
    assert m_enrich.call_count == 2


def test_add_type_ignore(tmp_path: Path):
    """Test add_type_ignore function."""
    from stubber.commands.stdlib_stubs_cmd import add_type_ignore

    # Create a test file
    stdlib_path = tmp_path / "stdlib"
    stdlib_path.mkdir()
    test_file = stdlib_path / "os.pyi"
    test_file.write_text("path = _path\ndef other(): pass")

    # Run the function
    add_type_ignore(stdlib_path)

    # Verify type ignore was added
    content = test_file.read_text()
    assert "# type: ignore" in content
    assert "path = _path  # type: ignore" in content


def test_comment_out_lines(tmp_path: Path):
    """Test comment_out_lines function."""
    from stubber.commands.stdlib_stubs_cmd import comment_out_lines

    # Create a test file
    stdlib_path = tmp_path / "stdlib"
    stdlib_path.mkdir()
    test_file = stdlib_path / "asyncio.pyi"
    test_file.write_text("from .subprocess import *\nother_line")

    # Run the function
    comment_out_lines(stdlib_path)

    # Verify line was commented out
    content = test_file.read_text()
    assert "# from .subprocess import *" in content


def test_change_lines(tmp_path: Path):
    """Test change_lines function."""
    from stubber.commands.stdlib_stubs_cmd import change_lines

    # Create a test file
    stdlib_path = tmp_path / "stdlib"
    stdlib_path.mkdir()
    test_file = stdlib_path / "ssl.pyi"
    test_file.write_text("def create_default_context(): pass\nother_line")

    # Run the function
    change_lines(stdlib_path)

    # Verify line was changed
    content = test_file.read_text()
    assert "def __mpy_has_no_create_default_context" in content


def test_update_typing_pyi(tmp_path: Path):
    """Test update_typing_pyi function."""
    from stubber.commands.stdlib_stubs_cmd import update_typing_pyi

    # Create paths
    rootpath = tmp_path / "root"
    dist_stdlib_path = tmp_path / "dist"

    # Run the function (currently does nothing, but should not error)
    update_typing_pyi(rootpath, dist_stdlib_path)


@pytest.mark.mocked
def test_cmd_stdlib_build_error(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with build error."""
    runner = CliRunner()

    # Mock version
    mocker.patch(
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

    # Mock subprocess to raise error
    import subprocess

    mocker.patch(
        "stubber.commands.stdlib_stubs_cmd.subprocess.check_call",
        side_effect=subprocess.CalledProcessError(1, "uv build", stderr="Build failed"),
    )

    # Mock CONFIG
    fake_config = mocker.MagicMock()
    fake_config.stub_path = tmp_path / "stubs"
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    pyproject = tmp_path / "publish" / "micropython-stdlib-stubs" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[tool.poetry]\nname='test'\n")

    # Run with build
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--build", "--no-merge", "--no-update"],
    )

    # Should fail with error message
    assert result.exit_code != 0
    assert "Build failed" in result.output or "Error" in result.output


@pytest.mark.mocked
def test_cmd_stdlib_missing_pyproject(mocker: MockerFixture, tmp_path: Path):
    """Test stdlib command with missing pyproject.toml."""
    runner = CliRunner()

    # Mock version
    mocker.patch(
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
    fake_config.repo_path = tmp_path / "repos"
    fake_config.typeshed_path = Path("typeshed")
    mocker.patch("stubber.commands.stdlib_stubs_cmd.CONFIG", fake_config)

    # Create necessary directories but NOT pyproject.toml
    reference_path = tmp_path / "reference"
    reference_path.mkdir(parents=True)

    stdlib_path = tmp_path / "publish" / "micropython-stdlib-stubs" / "stdlib"
    stdlib_path.mkdir(parents=True, exist_ok=True)

    # Run with build
    result = runner.invoke(
        stubber.stubber_cli,
        ["stdlib", "--build", "--no-merge", "--no-update"],
    )

    # Should fail with error about missing pyproject.toml
    assert result.exit_code != 0
    assert "pyproject.toml" in result.output.lower() or "error" in result.output.lower()
