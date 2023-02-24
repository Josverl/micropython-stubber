"""
POC to create a variants of createstubs.py
"""

import subprocess
import tempfile
from typing import List, Union
import libcst as cst
import libcst.codemod as codemod
from pathlib import Path

from stubber.codemod.board import CreateStubsCodemod, CreateStubsVariant
from stubber.codemod.modify_list import ListChangeSet

from loguru import logger as log

from stubber.utils.post import run_black
from stubber.minify import minify, cross_compile

ALL_VARIANTS = [CreateStubsVariant.BASE, CreateStubsVariant.MEM, CreateStubsVariant.DB, CreateStubsVariant.LVGL]


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
    cmd = ["pipx", "run", f"mpy-cross=={version}"] if version else ["pipx", "run", "mpy-cross"]
    # Add params
    cmd += ["-O2", str(source_file), "-o", str(target), "-s", "createstubs.py"]
    log.trace(" ".join(cmd))
    result = subprocess.run(cmd)  # , capture_output=True, text=True)

    if result.returncode == 0:
        log.debug(f"mpy-cross compiled to    : {target.name}")
    else:
        log.error("mpy-cross failed to compile:")
    return result.returncode


def create_variants(base_path: Path, make_variants: List[CreateStubsVariant] = ALL_VARIANTS, version: str = ""):
    """Create variants of createstubs.py"""
    ctx = codemod.CodemodContext()
    base_file = base_path / "createstubs.py"
    log.info(f"Reading : {base_file}")
    base_txt = (base_path / "createstubs.py").read_text()
    base_module = cst.parse_module(base_txt)

    for var in make_variants:
        # Transform base to createstubs.py variant

        suffix = "" if var == CreateStubsVariant.BASE else f"_{var.value}"

        variant_path = base_path / f"createstubs{suffix}.py"
        minified_path = base_path / f"createstubs{suffix}_min.py"
        mpy_path = base_path / f"createstubs{suffix}_mpy.mpy"  # intentional

        if var != CreateStubsVariant.BASE:
            # No need to create base variant as it is the same as the base file
            log.info(f"Transforming to {var.value} variant")
            cm = CreateStubsCodemod(ctx, variant=var)
            variant = cm.transform_module(base_module)

            # write low_mem_variant.code to file
            log.info(f"Write variant {var.value} to {variant_path}")
            with open(variant_path, "w") as f:
                f.write(variant.code)

            # format file with black
            run_black(variant_path, capture_output=True)
            # TODO: check with pyright if it is valid python

        # Minify file with pyminifier
        log.info(f"\nMinifying to {minified_path.name}")
        minify(variant_path, minified_path, keep_report=True, diff=False)

        # str -> path
        # read minified file
        minified_txt = minified_path.read_text()
        cross_compile(minified_txt, mpy_path, version=version)


# read base createstubs.py
base_path = Path.cwd() / "src" / "stubber" / "board"
create_variants(base_path)


if 0:
    # custom modules (and skip defaults).
    custom_stubs = ListChangeSet.from_strings(add=["mycoolpackage", "othermodule"], replace=True)
    custom_variant = CreateStubsCodemod(ctx, modules=custom_stubs).transform_module(base_module)

    print(custom_variant.code)
