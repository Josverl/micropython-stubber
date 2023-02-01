""" 
Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking 
using a custom-built parser to read and process the micropython RST files
"""

import os
from pathlib import Path
from typing import  List, Optional

from loguru import logger as log

from stubber.utils.post import run_autoflake, run_black

from stubber import utils
from stubber.rst import (
    DOCSTUB_SKIP,
    U_MODULES,
)
from stubber.rst.reader import RSTWriter



def generate_from_rst(
    rst_path: Path,
    dst_path: Path,
    v_tag: str,
    release: Optional[str] = None,
    pattern: str = "*.rst",
    suffix=".py",
) -> int:
    # sourcery skip: remove-redundant-exception, simplify-single-exception-tuple
    if not dst_path.exists():
        dst_path.mkdir(parents=True)
    if not release:
        release = v_tag
    # skip
    #  - index,
    # - modules with a . in the stem :  module.xxx.rst is included in module.py

    files = get_rst_sources(rst_path, pattern)

    # simplify debugging
    # files = [f for f in files if f.name == "collections.rst"]

    clean_destination(dst_path)
    make_docstubs(dst_path, v_tag, release, suffix, files)

    run_autoflake(dst_path, progress_pyi=True)
    run_black(dst_path)

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

def clean_destination(dst_path):
    """Remove all .py/.pyi files in desination folder to avoid left-behinds"""
    for f in dst_path.rglob(pattern="*.py*"):
        try:
            os.remove(f)
        except (OSError, PermissionError):
            pass

def get_rst_sources(rst_path:Path, pattern:str) -> List[Path]:
    """Get the list of rst files to process"""	
    files = [f for f in rst_path.glob(pattern) if f.stem != "index" and "." not in f.stem]

    # - excluded modules, ones that offer little advantage  or cause much problems
    files = [f for f in files if f.name not in DOCSTUB_SKIP]
    return files

def make_docstubs(dst_path:Path, v_tag:str, release:str,  suffix:str, files:List[Path]):
    """Create the docstubs"""

    for file in files:
        reader = RSTWriter(v_tag)
        reader.source_release = release
        log.debug(f"Reading: {file}")
        reader.read_file(file)
        reader.parse()
        if file.stem in U_MODULES:
            # create umod.py file and mod.py file
            reader.write_file((dst_path / ("u" + file.name)).with_suffix(suffix))
        reader.write_file((dst_path / file.name).with_suffix(suffix))
        del reader
