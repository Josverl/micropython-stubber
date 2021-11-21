#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pre/Post Processing for createstubs.py"""
import argparse
import itertools
import sys
from pathlib import Path
import subprocess

try:
    import python_minifier
except ImportError:
    python_minifier = None

ROOT = Path(__file__).parent
source_script = ROOT / "board" / "createstubs.py"
destination_script = ROOT / "minified" / "createstubs.py"


def edit_lines(content, edits, show_diff=False):
    """Edit string by list of edits

    Args:
        content (str): content to edit
        edits ([(str, str)]): List of edits to make.
            The first string in the tuple represents
            the type of edit to make, can be either:
                comment - comment text out (removed on minify)
                rprint - replace text with print
                rpass - replace text with pass
            The second string is the matching text to replace
        show_diff (bool, optional): Prints diff of each edit.
            Defaults to False.

    Returns:
        str: edited string
    """

    def comment(l, x):
        return l.replace(x, f"# {x}")

    def rprint(l, x):  # lgtm [py/unused-local-variable] pylint: disable= unused-variable
        split = l.split("(")
        if len(split) > 1:
            return l.replace(split[0].strip(), "print")
        return l.replace(x, f"print")

    def rpass(l, x):  # lgtm [py/unused-local-variable] pylint: disable= unused-variable
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
        while not open_cnt == close_cnt:
            look_ahead = l_index + ahead_index
            ahead_index += 1
            next_l = content[look_ahead]
            open_cnt += next_l.count("(")
            close_cnt += next_l.count(")")
        if ahead_index > 1:
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
                    if show_diff:
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


def minify_script(source_script: Path, keep_report=True, show_diff=False):
    """minifies createstubs.py

    Args:
        keep_report (bool, optional): Keeps single report line in createstubs
            Defaults to True.
        show_diff (bool, optional): Print diff from edits. Defaults to False.

    Returns:
        str: minified source text
    """

    edits = [
        ("comment", "print"),
        ("comment", "import logging"),
        # first full
        ("comment", "self._log ="),
        ("comment", "self._log("),
        ("comment", "self._log.debug"),
        ("comment", "self._log.warning"),
        ("comment", "self._log.info"),
        ("comment", "self._log.error"),
        # then short versions
        ("comment", "_log ="),
        ("comment", "_log.debug"),
        ("comment", "_log.warning"),
        ("comment", "_log.info"),
        ("comment", "_log.error"),
    ]
    if keep_report:
        report = (
            "rprint",
            ('self._log.info("Stub module: {:<20} to file:' ' {:<55} mem:{:>5}".' "format(module_name, file_name, m1))"),
        )
        clean = (
            "rprint",
            'self._log.info("Clean/remove files in folder: {}".format(path))',
        )
        edits.insert(0, report)
        edits.insert(1, clean)

    with source_script.open("r") as f:
        if not python_minifier:
            raise Exception("python_minifier not available")

        content = f.read()

        content = edit_lines(content, edits, show_diff=show_diff)

        source = python_minifier.minify(
            content,
            filename=source_script.name,
            combine_imports=True,
            remove_literal_statements=True,  # no Docstrings
            remove_annotations=True,  # not used runtime anyways
            hoist_literals=True,  # remove redundant strings
            rename_locals=True,  # short names save memory
            preserve_locals=["stubber"],  # names to keep
            rename_globals=True,  # short names save memory
            # keep these globals to allow testing/mocking to work agains the minified version
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
    print(f"Original length : {len(content)}")
    print(f"Minified length : {len(source)}")
    print(f"Reduced by      : {len(content)-len(source)} ")
    return source


def cli_minify(**kwargs):
    """minify cli handler"""
    source_path: Path = kwargs.pop("source")
    print(f"\nMinifying {source_path}...")
    out: Path = kwargs.pop("output")
    if not python_minifier:
        print("python_minifier is required to minify createstubs.py\n")
        print("Please install via:\n  pip install python_minifier")
        sys.exit(1)
    with out.open("w+") as f:
        report = kwargs.pop("no_report")
        diff = kwargs.pop("diff")

        source = minify_script(source_script=source_path, keep_report=report, show_diff=diff)
        f.write(source)

    print("Minified file written to :", out)
    result = subprocess.run(["mpy-cross", "-O2", str(out)])
    if result.returncode == 0:
        print("mpy-cross compiled to    :", out.with_suffix(".mpy"))

    print("\nDone!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre/Post Processing for createstubs.py")

    parser.set_defaults(func=None)
    parser.add_argument(
        "-s",
        "--source",
        help="Specify source file to read from. Defaults to {}".format(source_script),
        type=Path,
        default=source_script,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Specify file to output to. Defaults to {}".format(destination_script),
        type=Path,
        default=destination_script,
    )
    subparsers = parser.add_subparsers(help="Command to execute")

    minify_parser = subparsers.add_parser("minify", help=("Create minified version of createstubs.py"))
    minify_parser.add_argument("-d", "--diff", help="Print diff report from minify", action="store_true")
    minify_parser.add_argument(
        "-n",
        "--no-report",
        help=("Disables all output from createstubs.py." " Use if your having memory related issues."),
        action="store_false",
    )
    minify_parser.set_defaults(func=cli_minify)

    args = parser.parse_args()
    if not args.func:
        parser.print_help()
    else:
        args.func(**vars(args))
