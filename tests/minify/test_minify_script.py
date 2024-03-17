import pytest
from _pytest.python_api import RaisesContext

from stubber.minify import get_whitespace_context, minify_script
pytestmark = [pytest.mark.stubber]

@pytest.mark.parametrize(
    "content, index, expected",
    [
        # Happy path tests
        (
            ["    line 1", "line 2", "  line 3"],
            1,
            [0, 2],
        ),
        (
            ["line 1", "line 2", "line 3", "line 4"],
            1,
            [0, 0],
        ),
        (
            ["line 1", "line 2", "line 3"],
            2,
            [0, 0],
        ),
        # Edge cases
        (
            [],
            0,
            pytest.raises(ValueError),
        ),
        (
            ["line 1"],
            1,
            [0, 0],
        ),
        (
            ["line 1", "line 2"],
            2,
            pytest.raises(IndexError),
        ),
    ],
)
def test_get_whitespace_context(content, index, expected):
    # Arrange

    # Act
    if isinstance(expected, RaisesContext):
        # error expected
        with expected as exc_info:
            result = list(get_whitespace_context(content, index))
        return

    else:
        result = list(get_whitespace_context(content, index))

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "source_script, expected, keep_report",
    [
        # Happy path tests
        (
            ["#0", "__version__ = 1", "print('Hello, World!')", ""],
            ["__version__=1", "print('Hello, World!')"],
            True,
        ),
        (
            ["#1", "__version__ = 1"],
            # ["#1", "__version__ = 1"],
            ["__version__=1"],
            # "\n".join(["__version__=1"]),
            True,
        ),
        (
            ["#2", "print('Debug: Hello, World!')"],
            ["print('Debug: Hello, World!')"],
            True,
        ),
        (
            ["#3", 'print("Debug: Hello, World!")'],
            ["print('Debug: Hello, World!')"],
            True,
        ),
    ],
)
def test_minify_script(source_script, expected, keep_report):
    # Arrange
    source = "\n".join(source_script)

    # Act
    if isinstance(expected, RaisesContext):
        with expected as exc_info:
            minify_script(source, keep_report, diff=False)
    else:
        result = minify_script(source, keep_report, diff=True)

        result = result.split("\n")
        assert len(result) == len(expected), "Lengths do not match"
        for i, line in enumerate(result):
            assert expected[i] == line
