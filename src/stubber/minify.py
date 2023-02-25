"""
Processing for createstubs.py
Minimizes and cross-compiles a MicroPyton file.
"""
import io
import itertools
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Union, IO
from contextlib import ExitStack

from loguru import logger as log

import python_minifier

# Type Aliases for minify
StubSource = Union[Path, str, io.IOBase]
StubDest = Union[Path, io.IOBase]
LineEdits = List[Tuple[str, str]]


def edit_lines(content: str, edits: LineEdits, diff: bool = False):
    # sourcery skip: no-long-functions
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

    def comment(l: str, x: str):
        """Comment out line, so it will be removed on minify"""
        return l.replace(x, f"# {x}")

    def rprint(l: str, x: str):  # type: ignore
        """Replace (logging) with print"""
        split = l.split("(")
        if len(split) > 1:
            return l.replace(split[0].strip(), "print")
        return l.replace(x, "print")

    def rpass(l: str, x: str):  # type: ignore
        """Replace with pass"""
        return l.replace(x, "pass")

    def get_whitespace_context(content: List[str], index: int):
        """Get whitespace count of lines surrounding index"""

        def count_ws(line: str):
            return sum(1 for _ in itertools.takewhile(str.isspace, line))

        lines = content[index - 1 : index + 2]
        context = (count_ws(l) for l in lines)
        return context

    def handle_multiline(content: List[str], index: int):
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
        while open_cnt != close_cnt:  # pragma: no cover
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

    def handle_try_except(content: List[str], index: int):
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
    content_l = content.splitlines(keepends=True)
    for line in content_l:
        _line = line
        for edit, text in edits:
            if text in line:
                if edit == "comment":
                    l_index = content_l.index(line)
                    # Check if edit spans multiple lines
                    mline = handle_multiline(content_l, l_index)
                    if mline:
                        multilines.update(mline)
                        break
                    # Check if line is only statement in try/except
                    if handle_try_except(content_l, l_index):
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


def minify_script(source_script: StubSource, keep_report: bool = True, diff: bool = False) -> str:
    """
    Minifies createstubs.py and variants

    Args:
    source_script:
        - (str): content to edit
        - (Path): path to file to edit
        - (io.IOBase): file-like object to edit
    keep_report (bool, optional): Keeps single report line in createstubs
            Defaults to True.
    diff (bool, optional): Print diff from edits. Defaults to False.

    Returns:
        str: minified source text
    """

    source_content = ""
    if isinstance(source_script, Path):
        source_content = source_script.read_text()
    elif isinstance(source_script, (io.StringIO, io.TextIOWrapper)):
        source_content = "".join(source_script.readlines())
    elif isinstance(source_script, str):  # type: ignore
        source_content = source_script
    else:
        raise TypeError(f"source_script must be str, Path, or file-like object, not {type(source_script)}")

    if not source_content:
        raise ValueError("No source content")

    edits: LineEdits = [
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
        # insert report keepers after the comment modifiers
        edits[2:2] = [
            # keepers
            ("rprint", 'self._log.info("Stub module: '),
            ("rprint", 'self._log.warning("{}Skip module:'),
            ("rprint", 'self._log.info("Clean/remove files in folder:'),
            ("rprint", 'self._log.info("Created stubs for'),
        ]

    content = edit_lines(source_content, edits, diff=diff)

    source = python_minifier.minify(
        content,
        filename=getattr(source_script, "name", None),
        combine_imports=True,
        remove_literal_statements=True,  # no Docstrings
        remove_annotations=True,  # not used runtime anyways
        hoist_literals=True,  # remove redundant strings
        rename_locals=True,  # short names save memory
        preserve_locals=["stubber", "path"],  # names to keep
        rename_globals=True,  # short names save memory
        # keep these globals to allow testing/mocking to work against the minified not compiled version
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
    source: StubSource,
    target: StubDest,
    keep_report: bool = True,
    diff: bool = False,
):
    """Minifies and compiles a script"""
    source_buf = None
    target_buf = None

    with ExitStack() as stack:

        if isinstance(source, Path):
            source_buf = stack.enter_context(source.open("r"))
        elif isinstance(source, io.IOBase):
            source_buf = source
        else:
            source_buf = io.StringIO(source)

        if isinstance(target, Path):
            if target.is_dir():
                if isinstance(source, Path):
                    target = target / source.name
                else:
                    target = target / "minified.py"  # or raise error?
            target_buf = stack.enter_context(target.open("w+"))
        elif isinstance(target, io.IOBase):  # type: ignore
            target_buf = target
        try:
            minified = minify_script(source_script=source_buf, keep_report=keep_report, diff=diff)
            target_buf.write(minified)
        except Exception as e:  # pragma: no cover
            log.exception(e)
    return 0


def cross_compile(
    source: Union[Path, str],
    target: Path,
    version: str = "",
):  # sourcery skip: assign-if-exp
    """Runs mpy-cross on a (minified) script"""
    temp_file = None
    if isinstance(source, Path):
        source_file = source
    else:
        # create a temp file and write the source to it
        _, temp_file = tempfile.mkstemp(suffix=".py", prefix="mpy_cross_")
        temp_file = Path(temp_file)
        temp_file.write_text(source)
        source_file = temp_file
    if version:
        cmd = ["pipx", "run", f"mpy-cross=={version}"]
    else:
        cmd = ["mpy-cross"]
    # Add params
    cmd += ["-O2", str(source_file), "-o", str(target), "-s", "createstubs.py"]
    log.trace(" ".join(cmd))
    result = subprocess.run(cmd)  # , capture_output=True, text=True)

    if result.returncode == 0:
        log.debug(f"mpy-cross compiled to    : {target.name}")
    else:
        log.error("mpy-cross failed to compile:")
    return result.returncode


def save_to_tempfile(target_buf: StubDest, minified: str):
    "Save IO buffer to a temp file"
    _, temp_file = tempfile.mkstemp()
    temp_file = Path(temp_file)
    assert not isinstance(target_buf, Path), "target_buf must be a file path or file object"
    target_buf.seek(0)
    temp_file.write_text(minified)
    return temp_file
