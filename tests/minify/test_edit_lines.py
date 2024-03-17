import pytest
from _pytest.python_api import RaisesContext

from stubber.minify import edit_lines
pytestmark = [pytest.mark.stubber]
standard_edits = [
    ("keepprint", "print('Debug: "),
    ("keepprint", "print('DEBUG: "),
    ("keepprint", 'print("Debug: '),
    ("keepprint", 'print("DEBUG: '),
    ("comment", "print("),
    ("comment", "import logging"),
    # report keepers may be inserted here
    # do report errors
    ("rprint", "self._log.error"),
    ("rprint", "_log.error"),
]


@pytest.mark.parametrize(
    "edits, content, expected",
    [
        # Happy path tests
        (
            [("comment", "print")],
            "print('Hello, World!')",
            "# print('Hello, World!')",
        ),
        (
            [("comment", "import logging"), ("rprint", "logging.info")],
            """\
                import logging
                logging.info('Message')
            """,
            """\
                # import logging
                print('Message')
            """,
        ),
        (
            [("comment", "self._log.debug")],
            """\
                if condition:
                    self._log.debug('Message')
            """,
            """\
                # if condition:
                    # self._log.debug('Message')
            """,
        ),
        # Edge cases
        (
            [("comment", "print")],
            "",
            "",
        ),
        (
            [("comment", "print")],
            "print('Hello, World!')",
            "# print('Hello, World!')",
        ),
        (
            [("comment", "self._log.debug")],
            """\
                try:
                    something()
                except:
                    self._log.debug('Message')
            """,
            """\
                try:
                    something()
                except:
                    pass
            """,
        ),
        (
            [("comment", "invalid")],
            "print('Hello, World!')",
            "print('Hello, World!')",
        ),
        # Keep Debug Report
        (
            [("keepprint", "print('DEBUG: "), ("comment", "print(")],
            "print('DEBUG: Hello, World!')",
            "print ('DEBUG: Hello, World!')",
        ),
        (
            standard_edits,
            "print('DEBUG: Hello, World!')",
            "print ('DEBUG: Hello, World!')",
        ),
    ],
)
def test_edit_lines(content, edits, expected):
    # Arrange
    diff = True
    # Act
    if isinstance(expected, RaisesContext):
        with expected:
            result = edit_lines(content, edits, diff)
    else:
        result = edit_lines(content, edits, diff)

    # Assert
    assert result == expected
