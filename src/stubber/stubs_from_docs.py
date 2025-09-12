"""
Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking
using a custom-built parser to read and process the micropython RST files
"""

import os
from pathlib import Path
from typing import List, Optional

from mpflash.logger import log

from stubber import utils
from stubber.modcat import U_MODULES
from stubber.rst import DOCSTUB_SKIP
from stubber.rst.reader import RSTWriter


def generate_from_rst(
    rst_path: Path,
    dst_path: Path,
    v_tag: str,
    release: Optional[str] = None,
    pattern: str = "*.rst",
    suffix: str = ".pyi",
    black: bool = True,
    autoflake: bool = True,
    clean_rst: bool = True,
) -> int:
    dst_path.mkdir(parents=True, exist_ok=True)
    if not release:
        release = v_tag
    # skip
    #  - index,
    # - modules with a . in the stem :  module.xxx.rst is included in module.py

    files = get_rst_sources(rst_path, pattern)

    # reduce files for test/debugging
    # files = [f for f in files if "errno" in f.name]

    clean_destination(dst_path)
    make_docstubs(dst_path, v_tag, release, suffix, files, clean_rst=clean_rst)

    log.info("::group:: start post processing of retrieved stubs")
    # do not run stubgen
    utils.do_post_processing([dst_path], stubgen=False, format=black, autoflake=autoflake)

    # Generate a module manifest for the docstubs
    utils.make_manifest(
        folder=dst_path,
        family="micropython",
        version=utils.clean_version(v_tag),
        release=release,
        port="-",
        stubtype="documentation",
    )
    return len(files)


def clean_destination(dst_path: Path):
    """Remove all .py/.pyi files in desination folder to avoid left-behinds"""
    for f in dst_path.rglob(pattern="*.py*"):
        try:
            os.remove(f)
        except OSError:
            pass


def get_rst_sources(rst_path: Path, pattern: str) -> List[Path]:
    """Get the list of rst files to process"""
    files = [f for f in rst_path.glob(pattern) if f.stem != "index"]  # and "." not in f.stem]

    # - excluded modules, ones that offer little advantage  or cause much problems
    files = [f for f in files if f.name not in DOCSTUB_SKIP]
    return files


def make_docstubs(
    dst_path: Path,
    v_tag: str,
    release: str,
    suffix: str,
    files: List[Path],
    clean_rst: bool,
):
    """Create docstubs from the list of rst files"""

    for file in files:
        make_docstub(file, dst_path, v_tag, release, suffix, clean_rst)

    for name in U_MODULES:
        # create a file "umodule.pyi" for each module
        # and add a line : from module import *
        # this is to allow the use of the u modules in the code

        # create the file
        target = dst_path / f"u{name}.pyi"
        with open(target, "w") as f:
            f.write(f"# {name} module\n")
            f.write("# Allow the use of micro-module notation \n\n")
            f.write(f"from {name} import *  # type: ignore\n")
            f.flush()


def make_docstub(
    file: Path,
    dst_path: Path,
    v_tag: str,
    release: str,
    suffix: str,
    clean_rst: bool,
):
    """Create a docstub from a single rst file"""
    reader = RSTWriter(v_tag)
    reader.clean_rst = clean_rst
    reader.source_release = release
    log.debug(f"Reading: {file}")
    reader.read_file(file)
    reader.parse()

    if "." in file.stem:
        target = dst_path / f"{(file.stem).replace('.', '/')}{suffix}"
    else:
        target = dst_path / file.stem / f"__init__{suffix}"

    reader.write_file(target)
    del reader
