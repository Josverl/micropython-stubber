"""
Processing for createstubs.py
Minimizes and cross-compiles a MicroPyton file.
"""

import itertools
import subprocess
import tempfile
from contextlib import ExitStack
from io import BytesIO, IOBase, StringIO, TextIOWrapper
from pathlib import Path
from typing import List, Tuple, Union

try:
    import python_minifier
except ImportError:
    python_minifier = None

from mpflash.logger import log

from mpflash.versions import SET_PREVIEW, V_PREVIEW

# Type Aliases for minify
StubSource = Union[Path, str, StringIO, TextIOWrapper]
XCompileDest = Union[Path, BytesIO]
LineEdits = List[Tuple[str, str]]


def get_whitespace_context(content: List[str], index: int):
    """Get whitespace count of lines surrounding index"""
    if not content:
        raise ValueError()
    if index < 0 or index > len(content):
        raise IndexError()
    if len(content) == 1:
        return [0, 0]

    def count_ws(line: str):
        return sum(1 for _ in itertools.takewhile(str.isspace, line))

    lines = content[max(0, index) : min(index + 2, len(content))]
    context = [count_ws(l) for l in lines]
    if len(context) < 2:
        context.append(context[0])
    return context


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

    def keepprint(l: str, x: str):  # type: ignore
        """Replace 'print' with 'print '"""
        return l.replace("print(", "print (")

    def rpass(l: str, x: str):  # type: ignore
        """Replace with pass"""
        return l.replace(x, "pass")

    def handle_multiline(content: List[str], index: int):
        """Handles edits that require multiline comments

        Example:
            self.log.debug("info: {} {}".format(
                1,
                2
            ))
        Here, only commenting out the first self.log line will raise
        an error. So this function returns all lines that need to
        be commented out instead.

        It also checks for situations such as this:
            if condition:
                self.log.debug('message')

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
        line_ws, post_ws = get_whitespace_context(content, index)
        prev_words = prev.strip().strip(":").split()
        check = any(
            t
            in (
                "if",
                "else",
            )
            for t in prev_words
        )
        return range(index - 1, index + 1) if check and line_ws != post_ws else None

    def handle_try_except(content: List[str], index: int) -> bool:
        """Checks if line at index is in try/except block

        Handles situations like this:
            try:
                something()
            except:
                self.log.debug('some message')

        Simply removing the self.log call would create a syntax error,
        which is what this function checks for.

        """
        prev = content[index - 1]
        line_ws, post_ws = get_whitespace_context(content, index)
        return "except" in prev and line_ws != post_ws

    lines = []
    multilines = set()
    content_l = content.splitlines(keepends=True)
    for line in content_l:
        _line = line
        for edit_action, match_text in edits:
            if match_text in line:
                if edit_action == "comment":
                    l_index = content_l.index(line)
                    # Check if edit spans multiple lines
                    mline = handle_multiline(content_l, l_index)
                    if mline:
                        multilines.update(mline)
                        break
                    # Check if line is only statement in try/except
                    if handle_try_except(content_l, l_index):
                        edit_action = "rpass"
                        match_text = line.strip()
                func = eval(edit_action)  # pylint: disable= eval-used
                line = func(line, match_text)
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
        - (IOBase): file-like object to edit
    keep_report (bool, optional): Keeps single report line in createstubs
            Defaults to True.
    diff (bool, optional): Print diff from edits. Defaults to False.

    Returns:
        str: minified source text
    """

    source_content = ""
    if isinstance(source_script, Path):
        source_content = source_script.read_text(encoding="utf-8")
    elif isinstance(source_script, (StringIO, TextIOWrapper)):
        source_content = "".join(source_script.readlines())
    elif isinstance(source_script, str):  # type: ignore
        source_content = source_script
    else:
        raise TypeError(
            f"source_script must be str, Path, or file-like object, not {type(source_script)}"
        )

    if not source_content:
        raise ValueError("No source content")
    len_1 = len(source_content)

    if 0:
        min_source = reduce_log_print(keep_report, diff, source_content)
    else:
        min_source = source_content
    len_2 = len(min_source)

    if not python_minifier:
        log.warning("python_minifier not found, skipping minification")
    else:
        # use python_minifier to minify the source if it is successfully imported
        min_source = python_minifier.minify(
            min_source,
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
    len_3 = len(min_source)
    # if 1:
    #     # write to temp file for debugging
    #     with open("tmp_minified.py", "w+") as f:
    #         f.write(min_source)

    log.info(f"Original length : {len_1}")
    log.info(f"Reduced length  : {len_2}")
    log.info(f"Minified length : {len_3}")
    log.info(f"Reduced by      : {len_1-len_3} ")
    return min_source


def reduce_log_print(keep_report, diff, source_content):
    edits: LineEdits = [
        ("keepprint", "print('Debug: "),
        ("keepprint", "print('DEBUG: "),
        ("keepprint", 'print("Debug: '),
        ("keepprint", 'print("DEBUG: '),
        ("comment", "print("),
        ("comment", "import logging"),
        # report keepers may be inserted here
        # do report errors
        ("rprint", "self.log.error"),
        ("rprint", "log.error"),
    ]
    if keep_report:
        # insert report keepers after the comment modifiers
        edits += [
            # keepers
            ("rprint", 'self.log.info("Stub module: '),
            ("rprint", 'self.log.warning("{}Skip module:'),
            ("rprint", 'self.log.info("Clean/remove files in folder:'),
            ("rprint", 'self.log.info("Created stubs for'),
            ("rprint", 'self.log.info("Family: '),
            ("rprint", 'self.log.info("Version: '),
            ("rprint", 'self.log.info("Port: '),
            ("rprint", 'self.log.info("Board: '),
            # all others
            ("comment", "self.log"),
            ("comment", "_log."),
            ("comment", "_log ="),
        ]
    else:
        edits += [
            #  remove first full
            ("comment", "self.log ="),
            ("comment", "self.log("),
            ("comment", "self.log.debug"),
            ("comment", "self.log.info"),
            ("comment", "self.log.warning"),
            # then short versions
            ("comment", "_log ="),
            ("comment", "_log.debug"),
            ("comment", "_log.info"),
            ("comment", "_log.warning"),
        ] + edits

    content = edit_lines(source_content, edits, diff=diff)
    return content


def minify(
    source: StubSource,
    target: StubSource,
    keep_report: bool = True,
    diff: bool = False,
):
    """Minifies and compiles a script"""
    source_buf = None
    target_buf = None

    with ExitStack() as stack:
        if isinstance(source, Path):
            source_buf = stack.enter_context(source.open("r"))
        elif isinstance(source, (StringIO, str)):
            # different types of file-like objects are both acepted by minify_script
            source_buf = source
        else:
            raise TypeError(f"source must be str, Path, or file-like object, not {type(source)}")

        if isinstance(target, Path):
            if target.is_dir():
                if isinstance(source, Path):
                    target = target / source.name
                else:
                    target = target / "minified.py"  # or raise error?
            target_buf = stack.enter_context(target.open("w+"))
        elif isinstance(target, IOBase):  # type: ignore
            target_buf = target
        try:
            minified = minify_script(source_script=source_buf, keep_report=keep_report, diff=diff)
            target_buf.write(minified)
        except Exception as e:  # pragma: no cover
            log.exception(e)
    return 0


def cross_compile(
    source: StubSource,
    target: XCompileDest,
    version: str = "",
):  # sourcery skip: assign-if-exp
    """Runs mpy-cross on a (minified) script"""
    # Sources can be a file, a string, or a file-like object
    if isinstance(source, Path):
        source_file = source
    elif isinstance(source, str):
        # create a temp file and write the source to it
        source_file = write_to_temp_file(source)
    elif isinstance(source, StringIO):
        source_file = write_to_temp_file(source.getvalue())
    else:
        raise TypeError(f"source must be str, Path, or file-like object, not {type(source)}")

    _target = None
    if isinstance(target, Path):
        if target.is_dir():
            target = target / source.name if isinstance(source, Path) else target / "minified.mpy"
        _target = target.with_suffix(".mpy")
    else:
        # target must be a Path object
        _target = get_temp_file(suffix=".mpy")
    result = pipx_mpy_cross(version, source_file, _target)
    if result.stderr and "No matching distribution found for mpy-cross==" in result.stderr:
        log.warning(f"mpy-cross=={version} not found, using default version.")
        result = pipx_mpy_cross(V_PREVIEW, source_file, _target)

    if result.returncode == 0:
        log.debug(f"mpy-cross compiled to    : {_target.name}")
    else:
        log.error(f"mpy-cross failed to compile:{result.returncode} \n{result.stderr}")

    if isinstance(target, BytesIO):
        # copy the byte contents of the temp file to the target file-like object
        with _target.open("rb") as f:
            target.write(f.read())
        # _target.unlink()

    return result.returncode


def pipx_mpy_cross(version: str, source_file, _target):
    """Run mpy-cross using pipx"""

    log.info(f"Compiling with mpy-cross version: {version}")
    if version in SET_PREVIEW:
        version = ""
    if version:
        version = "==" + version

    cmd = ["pipx", "run", f"mpy-cross{version}"] if version else ["pipx", "run", "mpy-cross"]
    # Add params
    cmd += ["-O2", str(source_file), "-o", str(_target), "-s", "createstubs.py"]
    log.trace(" ".join(cmd))
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8"
    )  # Specify the encoding
    return result


def write_to_temp_file(source: str):
    """Writes a string to a temp file and returns the Path object"""
    _, temp_file = tempfile.mkstemp(suffix=".py", prefix="mpy_cross_")
    temp_file = Path(temp_file)
    temp_file.write_text(source)
    return temp_file


def get_temp_file(prefix: str = "mpy_cross_", suffix: str = ".py"):
    """Get temp file and returns the Path object"""
    _, temp_file = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    temp_file = Path(temp_file)
    return temp_file
