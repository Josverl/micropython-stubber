"""
Add missing methods to classes in the stubs that are documented in the docstubs

"""

from pathlib import Path

import libcst as cst
from mpflash.logger import log

from mpflash.versions import clean_version
from stubber.codemod.add_method import CallAdder, CallFinder
from stubber.utils.config import CONFIG
from stubber.utils.post import run_black


def add_machine_pin_call(merged_path: Path, version: str):
    """
    Add the __call__ method to the machine.Pin and pyb.Pin class
    in all pyb and machine/umachine stubs
    """
    # TODO: this should be done in the merge_docstubs.py to avoid needing to run black twice
    # and to avoid having to parse the file twice

    # first find the __call__ method in the default stubs
    mod_path = (
        CONFIG.stub_path / f"micropython-{clean_version(version, flat=True)}-docstubs/machine.pyi"
    )
    if not mod_path.exists():
        log.error(f"no docstubs found for {version}")
        return False
    log.trace(f"Parsing {mod_path} for __call__ method")
    source = mod_path.read_text(encoding="utf-8")
    module = cst.parse_module(source)

    call_finder = CallFinder()
    module.visit(call_finder)

    if call_finder.call_meth is None:
        log.error("no __call__ method found")
        return False

    # then use the CallAdder to add the __call__ method to all machine and pyb stubs
    mod_paths = [f for f in merged_path.rglob("*.*") if f.stem in {"machine", "umachine", "pyb"}]
    for mod_path in mod_paths:
        source = mod_path.read_text(encoding="utf-8")
        machine_module = cst.parse_module(source)
        new_module = machine_module.visit(CallAdder(call_finder.call_meth))
        mod_path.write_text(new_module.code, encoding="utf-8")
        run_black(mod_path)
    return True
