"""
 Processing for createstubs.py
 minimizes and cross-compiles a micropyton file.
"""
import itertools
import subprocess
from pathlib import Path
from typing import List, Tuple, Union

from loguru import logger as log

try:
    import python_minifier
except ImportError:  # pragma: no cover
    python_minifier = None


def edit_lines(content, edits, diff=False):
    """Edit string by list of edits

    Args:
        content (str): content to edit
        edits ([(str, str)]): List of edits to make.
            The first string in the tuple representsthe type of edit to make, can be either:
            - comment - comment text out (removed on minify)
            - rprint - replace text with print
            - rpass - replace text with pass
            The second string is the matching text to replace
        diff (bool, optional): Prints diff of each edit.
            Defaults to False.

    Returns:
        str: edited string
    """

    def comment(l, x):
        return l.replace(x, f"# {x}")

    def rprint(l, x):  # type: ignore # lgtm [py/unused-local-variable] pylint: disable= unused-variable
        split = l.split("(")
        if len(split) > 1:
            return l.replace(split[0].strip(), "print")
        return l.replace(x, f"print")

    def rpass(l, x):  # type: ignore # lgtm [py/unused-local-variable] pylint: disable= unused-variable
        return l.replace(x, f"pass")

    def get_whitespace_context(content, index):
        """Get whitespace count of lines surrounding index"""

        def count_ws(line):
            return sum(1 for _ in itertools.takewhile(str.isspace, line))

        lines = content[index - 1 : index + 2]
        context = (count_ws(l) for l in lines)
        return context

    def handle_multiline(content, index):
        """Handles edits that require multiline comments

        Example:
            self._log.debug("info: {} {}".format(
                1,
                2
            ))
        Here, only commenting out the first self._log line will raise
        an error. So this function returns all lines that need to
        be commented out instead.

        It also checks for situations such as this:
            if condition:
                self._log.debug('message')

        Here, since the only functionality of the conditional is the call log,
        both lines would be returned to comment out.

        """
        line = content[index]
        open_cnt = line.count("(")
        close_cnt = line.count(")")
        ahead_index = 1
        look_ahead = 0
        while not open_cnt == close_cnt:  # pragma: no cover
            look_ahead = l_index + ahead_index
            ahead_index += 1
            next_l = content[look_ahead]
            open_cnt += next_l.count("(")
            close_cnt += next_l.count(")")
        if ahead_index > 1:  # pragma: no cover
            return range(index, look_ahead + 1)
        prev = content[index - 1]
        _, line_ws, post_ws = get_whitespace_context(content, index)
        prev_words = prev.strip().strip(":").split()
        check = any(
            t
            in (
                "if",
                "else",
            )
            for t in prev_words
        )
        if check and line_ws != post_ws:
            return range(index - 1, index + 1)

    def handle_try_except(content, index):
        """Checks if line at index is in try/except block

        Handles situations like this:
            try:
                something()
            except:
                self._log.debug('some message')

        Simply removing the self._log call would create a syntax error,
        which is what this function checks for.

        """
        prev = content[index - 1]
        _, line_ws, post_ws = get_whitespace_context(content, index)
        if "except" in prev and line_ws != post_ws:
            return True

    lines = []
    multilines = set()
    content = content.splitlines(keepends=True)
    for line in content:
        _line = line
        for edit, text in edits:
            if text in line:
                if edit == "comment":
                    l_index = content.index(line)
                    # Check if edit spans multiple lines
                    mline = handle_multiline(content, l_index)
                    if mline:
                        multilines.update(mline)
                        break
                    # Check if line is only statement in try/except
                    if handle_try_except(content, l_index):
                        edit = "rpass"
                        text = line.strip()
                func = eval(edit)  # pylint: disable= eval-used
                line = func(line, text)
                if line != _line:
                    if diff:
                        print(f"\n- {_line.strip()}")
                        print(f"+ {line.strip()}")
                    break
        lines.append(line)
    for line_num in multilines:
        # Go back and comment out multilines
        line = lines[line_num]
        lines[line_num] = comment(line, line.strip())
    stripped = "".join(lines)
    return stripped


def minify_script(source_script: Path, keep_report=True, diff=False) -> str:
    """minifies createstubs.py

    Args:
        keep_report (bool, optional): Keeps single report line in createstubs
            Defaults to True.
        diff (bool, optional): Print diff from edits. Defaults to False.

    Returns:
        str: minified source text
    """

    edits: List[Tuple[str, str]] = [
        ("comment", "print"),
        ("comment", "import logging"),
        # report keepers may be inserted here
        # do report errors
        ("rprint", "self._log.error"),
        ("rprint", "_log.error"),
        #  remove first full
        ("comment", "self._log ="),
        ("comment", "self._log("),
        ("comment", "self._log.debug"),
        ("comment", "self._log.info"),
        ("comment", "self._log.warning"),
        # then short versions
        ("comment", "_log ="),
        ("comment", "_log.debug"),
        ("comment", "_log.info"),
        ("comment", "_log.warning"),
    ]
    if keep_report:
        edits[2:2] = [
            # keepers
            ("rprint", 'self._log.info("Stub module: '),
            ("rprint", 'self._log.warning("{}Skip module:'),
            ("rprint", 'self._log.info("Clean/remove files in folder:'),
            ("rprint", 'self._log.info("Created stubs for'),
        ]

    with source_script.open("r") as f:
        if not python_minifier:  # pragma: no cover
            raise Exception("python_minifier not available")

        content = f.read()

        content = edit_lines(content, edits, diff=diff)

        source = python_minifier.minify(
            content,
            filename=source_script.name,
            combine_imports=True,
            remove_literal_statements=True,  # no Docstrings
            remove_annotations=True,  # not used runtime anyways
            hoist_literals=True,  # remove redundant strings
            rename_locals=True,  # short names save memory
            preserve_locals=["stubber", "path"],  # names to keep
            rename_globals=True,  # short names save memory
            # keep these globals to allow testing/mocking to work against the minified version
            preserve_globals=[
                "main",
                "Stubber",
                "read_path",
                "get_root",
                "_info",
                "os",
                "sys",
                "__version__",
            ],
            # remove_pass=True,  # no dead code
            # convert_posargs_to_args=True, # Does not save any space
        )
    log.debug(f"Original length : {len(content)}")
    log.info(f"Minified length : {len(source)}")
    log.info(f"Reduced by      : {len(content)-len(source)} ")
    return source


def minify(
    source: Union[str, Path],
    target: Union[str, Path],
    keep_report: bool = True,
    diff: bool = False,
    cross_compile: bool = False,
):

    source = Path(source)
    target = Path(target)
    # if target is a folder , then append the filename
    if target.exists() and target.is_dir():
        target = target / source.name
    try:
        with target.open("w+") as f:
            minified = minify_script(source_script=source, keep_report=keep_report, diff=diff)
            f.write(minified)
    except Exception as e:  # pragma: no cover
        log.exception(e)

    log.debug("Minified file written to :", target)
    if cross_compile:
        result = subprocess.run(["mpy-cross", "-O2", str(target)])
        if result.returncode == 0:
            log.debug("mpy-cross compiled to    :", target.with_suffix(".mpy"))
        return result.returncode
    else:
        return 0
