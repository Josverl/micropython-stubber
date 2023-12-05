import subprocess
from pathlib import Path

from stubber.utils.post import run_black


def test_run_black(tmp_path, capsys):
    # Create a temporary file for testing
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def foo():\n    print('Hello, World!' )\n")

    # Run the black formatting
    return_code = run_black(test_file)

    # Check if black ran successfully
    assert return_code == 0

    # Check if the file content has been formatted
    formatted_content = test_file.read_text()
    assert formatted_content == 'def foo():\n    print("Hello, World!")\n'

    # Clean up the temporary file
    # test_file.unlink()


def test_run_black_capture_output(tmp_path, capsys):
    # Create a temporary file for testing
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def foo():\n    print('Hello, World!')\n")

    # Run the black formatting with capture_output enabled
    return_code = run_black(test_file, capture_output=True)

    # Check if black ran successfully
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
