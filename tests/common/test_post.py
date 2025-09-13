import pytest

pytestmark = [pytest.mark.stubber]

from stubber.utils.post import format_stubs


def test_run_formatter(tmp_path, capsys):
    # Create a temporary file for testing
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def foo():\n    print('Hello, World!' )\n")

    # Run the ruff formatting
    return_code = format_stubs(test_file)

    # Check if ruff format ran successfully
    assert return_code == 0

    # Check if the file content has been formatted
    formatted_content = test_file.read_text()
    assert formatted_content == 'def foo():\n    print("Hello, World!")\n'

    # Clean up the temporary file
    # test_file.unlink()


def test_run_formatter_capture_output(tmp_path, capsys):
    # Create a temporary file for testing
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def foo():\n    print('Hello, World!')\n")

    # Run the ruff formatting with capture_output enabled
    return_code = format_stubs(test_file, capture_output=True)

    # Check if ruff format ran successfully
    assert return_code == 0

    # Check if the file content has been formatted
    formatted_content = test_file.read_text()
    assert formatted_content == 'def foo():\n    print("Hello, World!")\n'

    # Check if the captured output is empty
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    # Clean up the temporary file
    test_file.unlink()
