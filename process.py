#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pre/Post Processing for createstubs.py

commands:
  minify                 Create minified version of createstubs.py

"""

import argparse
import re
import sys
from optparse import Values
from pathlib import Path

# Pyminifier Dep
token_utils = None
minification = None
try:
    from pyminifier import token_utils, minification
except ImportError:
    pass

ROOT = Path(__file__).parent
SCRIPT = ROOT / 'createstubs.py'
PATCHES = ROOT / 'patches'


def apply_patch(s, patch, revert=False):
    """
    Apply patch to string s to recover newer string.
    If revert is True, treat s as the newer string, recover older string.

    Credits:
    Isaac Turner 2016/12/05
    https://gist.github.com/noporpoise/16e731849eb1231e86d78f9dfeca3abc
    """
    _hdr_pat = re.compile(r"@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@")
    s = s.splitlines(True)
    p = patch.splitlines(True)
    t = ''
    i = sl = 0
    (midx, sign) = (1, '+') if not revert else (3, '-')
    while i < len(p) and not p[i].startswith("@@"):
        i += 1  # skip header lines
    while i < len(p):
        m = _hdr_pat.match(p[i])
        if not m:
            raise Exception("Bad patch -- regex mismatch [line "+str(i)+"]")
        l = int(m.group(midx))-1 + (m.group(midx+1) == '0')
        if sl > l or l > len(s):
            raise Exception("Bad patch -- bad line num [line "+str(i)+"]")
        t += ''.join(s[sl:l])
        sl = l
        i += 1
        while i < len(p) and p[i][0] != '@':
            if i+1 < len(p) and p[i+1][0] == '\\':
                line = p[i][:-1]
                i += 2
            else:
                line = p[i]
                i += 1
            if len(line) > 0:
                if line[0] == sign or line[0] == ' ':
                    t += line[1:]
                sl += (line[0] != sign)
    t += ''.join(s[sl:])
    return t


def edit_lines(content, edits):
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

    Returns:
        str: edited string
    """
    def comment(l, x): return l.replace(x, f"# {x}")
    def rprint(l, x): return l.replace(x, f"print")
    def rpass(l, x): return l.replace(x, f"pass")
    lines = []
    for line in content.splitlines(keepends=True):
        for edit, text in edits:
            func = eval(edit)
            line = func(line, text)
        lines.append(line)
    stripped = "".join(lines)
    return stripped


def minify_script(patches=None):
    """minifies createstubs.py

    Args:
        patches ([PathLike], optional): List of paths to patches to apply.
            Defaults to None.

    Returns:
        str: minified source text
    """
    patches = patches or []
    edits = [
        ("comment", "import logging"),
        ("comment", "self._log ="),
        ("rpass",
         'self._log.debug("could not del modules[{}]".format(module_name))'),
        ("comment", "self._log.debug"),
        ("rprint", "self._log.warning"),
        ("rprint", "self._log.info"),
        ("rprint", "self._log.error"),
    ]
    minopts = Values({'tabs': False})
    with SCRIPT.open('r') as f:
        content = f.read()
        for path in patches:
            with path.open('r') as p:
                content = apply_patch(content, p.read())
        content = edit_lines(content, edits)
        tokens = token_utils.listified_tokenizer(content)
        source = minification.minify(tokens, minopts)
    return source


def get_patches():
    """Iterate patch files"""
    for f in PATCHES.iterdir():
        yield (f.stem, f.resolve())


def cli_minify(**kwargs):
    """minify cli handler"""
    print("\nMinifying createstubs.py...")
    out = kwargs.pop("dest")
    patches = kwargs.pop("patches")
    patch_paths = []
    if not minification:
        print("\npyminification is required to minify createstubs.py\n")
        print("Please install via:\n  pip install pyminification")
        sys.exit(1)
    for name, path in patches:
        if path is None:
            print(f"Cannot find patch: {name}")
            print("\nAvailable Patches:")
            print("\n".join(p[0] for p in get_patches()))
            sys.exit(0)
        print(f"Applying Patch: {name}")
        patch_paths.append(path)
    with out.open('w+') as f:
        source = minify_script(patch_paths)
        f.write(source)
    print("\nDone!")
    print(f"Minified file written to: {out}")


if __name__ == "__main__":
    class HelpTextFormatter(argparse.RawDescriptionHelpFormatter):
        """Help Text Formatter
        Credit - https://stackoverflow.com/a/35925919
        """

        def __add_whitespace(self, idx, iWSpace, text):
            if idx == 0:
                return text
            return (" " * iWSpace) + text

    patches = list(get_patches())
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=HelpTextFormatter)
    parser.add_argument('command', nargs='+', help="Command to execute")
    parser.add_argument('-p', '--patch',
                        action='append',
                        type=lambda x:
                        next((p
                              for p in patches if p[0] == x), (x, None)),
                        help="Apply a patch to createstubs.py",
                        default=[]
                        )
    parser.add_argument(
        "-d", "--dest",
        help="Specify file to output to. Defaults to minified.py",
        type=Path,
        default=(ROOT / 'minified.py'))
    args = parser.parse_args()
    cmd = args.command.pop(0)
    func = eval(f"cli_{cmd}")
    func(patches=args.patch, opts=args.command, dest=args.dest)
