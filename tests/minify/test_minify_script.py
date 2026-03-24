import pytest
from _pytest.python_api import RaisesContext

from stubber.minify import fix_ternary_spacing, get_whitespace_context, minify_script, python_minifier

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
    # Skip minification test if no minifier tool is available
    if not python_minifier:
        pytest.skip("Python minifier not available")

    # Act
    if isinstance(expected, RaisesContext):
        # error expected
        with expected:
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
    # Skip minification test if no minifier tool is available
    if not python_minifier:
        pytest.skip("Python minifier not available")

    # Arrange
    source = "\n".join(source_script)

    # Act
    if isinstance(expected, RaisesContext):
        with expected:
            minify_script(source, keep_report, diff=False)
    else:
        result = minify_script(source, keep_report, diff=True)

        result = result.split("\n")
        assert len(result) == len(expected), "Lengths do not match"
        for i, line in enumerate(result):
            assert expected[i] == line


@pytest.mark.parametrize(
    "source, expected",
    [
        # f-string ternary without spaces (the bug from mpy-cross v1.18)
        (
            'B[\'ver\']=f"{B[A]}-{B[N]}"if B[N]else f"{B[A]}"',
            'B[\'ver\']=f"{B[A]}-{B[N]}" if B[N] else f"{B[A]}"',
        ),
        # string ternary without spaces
        (
            "B='hello'if b else'world'",
            "B='hello' if b else 'world'",
        ),
        # 'in' keyword adjacent to string
        (
            "if'_machine'in dir(a):pass",
            "if '_machine' in dir(a):pass",
        ),
        # 'not' keyword adjacent to string
        (
            "not'key'in a",
            "not 'key' in a",
        ),
        # 'in' adjacent to bracket
        (
            "a in(A,'c')",
            "a in (A,'c')",
        ),
        # Block if/else - should NOT be changed
        (
            "if x:pass\nelif y:pass\nelse:pass",
            "if x:pass\nelif y:pass\nelse:pass",
        ),
        # Already properly spaced - should NOT be changed
        (
            "x = 1 if True else 2",
            "x = 1 if True else 2",
        ),
        # 'not in' operator - should NOT change spacing
        (
            "A=a if a not in b else b",
            "A=a if a not in b else b",
        ),
        # List comprehension 'if' without space
        (
            "B=[A for A in range(10)if A>5]",
            "B=[A for A in range(10) if A>5]",
        ),
    ],
)
def test_fix_ternary_spacing(source, expected):
    """Test that fix_ternary_spacing adds required spaces around keywords for mpy-cross compatibility."""
    result = fix_ternary_spacing(source)
    assert result == expected


def test_minify_script_keyword_spacing():
    """Test that minify_script produces output with proper spaces around keywords (mpy-cross compatibility)."""
    import re

    if not python_minifier:
        pytest.skip("Python minifier not available")

    # Source with f-string ternary expressions that trigger the mpy-cross SyntaxError
    source = "\n".join([
        "def _format(info):",
        "    info['ver'] = f\"{info['version']}-{info['build']}\" if info['build'] else f\"{info['version']}\"",
        "    x = 'hello' if info['build'] else 'world'",
        "    return info",
    ])

    result = minify_script(source, keep_report=False)

    # Verify no keyword is directly adjacent to a non-whitespace character (mpy-cross incompatible)
    assert not re.search(r"(?<=\S)\b(if|else|in|not)\b", result), (
        "Minified output contains keywords without required spaces (breaks mpy-cross compatibility)"
    )
