"""Add (missing) __init__ methods to a class using a regex"""

from pathlib import Path
import re

# ref: https://extendsclass.com/regex/e6adb72

empty_classdef = r"(?P<indent1> ?)class\s*(?P<class>\s*.+\s*):(?P<LF>\r?\n)(?P<indent2> +)''\r?\n"
re_classdef = re.compile(empty_classdef, flags=re.MULTILINE)
repl_classdef = (
    r"\g<indent1>class \g<class>:\g<LF>\g<indent2>def __init__(self):\g<LF>\g<indent2>    ''\g<LF>\g<indent2>    pass\g<LF>\g<LF>"
)


def add_init_methods(filename:Path) -> int:
    """Add (missing) __init__ methods to a class using a regex
    this assumes the (incorrect) classdef format that has been used by stubbers prior to version 1.4.0
    and updates that to add the init.

    """
    found = 0
    with open(filename, mode="+r") as file:
        content = file.read()
        found = len(re_classdef.findall(content))
        content = re_classdef.sub(repl_classdef, content)
        # print(content)
        file.seek(0)
        file.write(content)
    return found


print("Add missing __init__ methods to stub classes")

for stubfile in Path("./micropython-stubs/stubs").glob(r"**/*.py"):
    print(stubfile, end=" ,")
    x = add_init_methods(stubfile)
    print(x)


for stubfile in Path("all_stubs").glob(r"**/*.py"):
    print(stubfile)
