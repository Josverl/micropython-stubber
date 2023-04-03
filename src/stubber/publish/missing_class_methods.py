"""
Add missing methods to classes in the stubs that are documented in the docstubs

"""
from pathlib import Path

import libcst as cst

from stubber.codemod.add_method import CallAdder
from stubber.utils.post import run_black


def add_machine_pin_call(merged_path: Path):
    """
    Add the __call__ method to the machine.Pin and pyb.Pin class
    in all pyb and machine/umachine stubs
    """
    mod_paths = [f for f in merged_path.rglob("*.*") if f.stem in {"machine", "umachine", "pyb"}]
    for mod_path in mod_paths:
        source = mod_path.read_text()
        machine_module = cst.parse_module(source)
        new_module = machine_module.visit(CallAdder())
        mod_path.write_text(new_module.code)
        run_black(mod_path)
