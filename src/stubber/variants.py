"""
Create all variants of createstubs.py
- and minify them 
- and cross compile them
"""

import shutil
from pathlib import Path
from typing import List, Optional

import libcst as cst
import libcst.codemod as codemod
from mpflash.logger import log

from stubber.codemod.board import CreateStubsCodemod, CreateStubsVariant
from stubber.codemod.modify_list import ListChangeSet  # type: ignore
from stubber.minify import cross_compile, minify
from stubber.update_module_list import update_module_list
from stubber.utils.post import run_black

ALL_VARIANTS = list(CreateStubsVariant)


def create_variants(
    base_path: Path,
    *,
    target_path: Optional[Path] = None,
    version: str = "",
    make_variants: List[CreateStubsVariant] = ALL_VARIANTS[:3],
    update_modules: bool = True,
):
    """
    Create variants of createstubs.py and optionally minify and cross compile them.

    Parameters
    ----------
    base_path : Path
        Path to the base createstubs.py file
    target_path : Path, optional
        Path to write the variants to, by default None
    version : str, optional
        Version of mpy-cross to use, by default uses the latest published version

    """
    if target_path is None:
        target_path = base_path
    if update_modules:
        update_module_list()

    ctx = codemod.CodemodContext()
    base_file = base_path / "createstubs.py"
    log.info(f"Reading : {base_file}")
    base_txt = (base_path / "createstubs.py").read_text(encoding="utf-8")
    base_module = cst.parse_module(base_txt)

    for var in make_variants:
        # Transform base to createstubs.py variant

        suffix = "" if var == CreateStubsVariant.BASE else f"_{var.value}"

        variant_path = target_path / f"createstubs{suffix}.py"
        minified_path = target_path / f"createstubs{suffix}_min.py"
        mpy_path = target_path / f"createstubs{suffix}_mpy.mpy"  # intentional

        if var == CreateStubsVariant.BASE and target_path != base_path:
            log.info(f"Copying base file to {variant_path}")
            variant_path.write_text(base_txt)
            # copy modules.txt to target_path
            shutil.copyfile(base_path / "modulelist.txt", target_path / "modulelist.txt")

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
        log.info(f"Minifying to {minified_path.name}")
        minify(variant_path, minified_path, keep_report=False, diff=False)

        # str -> path
        # read minified file
        minified_txt = minified_path.read_text(encoding="utf-8")
        cross_compile(minified_txt, mpy_path, version=version)


if __name__ == "__main__":
    # read base createstubs.py
    base_path = Path.cwd() / "src" / "stubber" / "board"
    create_variants(base_path)

    # if 0:
    #     # custom modules (and skip defaults).
    #     custom_stubs = ListChangeSet.from_strings(add=["mycoolpackage", "othermodule"], replace=True)
    #     custom_variant = CreateStubsCodemod(ctx, modules=custom_stubs).transform_module(base_module)

    #     print(custom_variant.code)
