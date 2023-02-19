"""
POC to create a variants of createstubs.py
"""

import libcst as cst
import libcst.codemod as codemod
from pathlib import Path

from stubber.codemod.board import CreateStubsCodemod, CreateStubsFlavor
from stubber.codemod.modify_list import ListChangeSet

from loguru import logger as log

# read base createstubs.py
base_path = Path.cwd() / "src" / "stubber" / "board"


ctx = codemod.CodemodContext()
base_file = base_path / "createstubs.py"
log.info(f"Reading : {base_file}")
base_txt = (base_path / "createstubs.py").read_text()
base_module = cst.parse_module(base_txt)


for var in [CreateStubsFlavor.LOW_MEM, CreateStubsFlavor.DB, CreateStubsFlavor.LVGL]:
    # Transform base to Low memory createstubs.py
    log.info(f"Transforming to {var.value} variant")
    cm = CreateStubsCodemod(ctx, flavor=var)
    variant = cm.transform_module(base_module)

    # write low_mem_variant.code to file
    fname = base_path / f"createstubs_{var.value}.py"
    log.info(f"Write variant {var.value} to {fname}")
    with open(fname, "w") as f:
        f.write(variant.code)

    #

    # format file with black
    # check with pyright if it is valid python

    # Minify file with pyminifier
    # cross compile for mpy version with mpy-cross


# # custom modules (and skip defaults).
# custom_stubs = ListChangeSet.from_strings(add=["mycoolpackage", "othermodule"], replace=True)
# custom_variant = CreateStubsCodemod(ctx, modules=custom_stubs).transform_module(base_module)

# print(custom_variant.code)
