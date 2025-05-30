""" 
Merge MCU stubs and docstubs into a single folder
"""

import shutil
from pathlib import Path
from typing import List, Optional, Union

from mpflash.logger import log
from stubber.codemod.enrich import enrich_folder
from stubber.merge_config import RM_MERGED, recreate_umodules, remove_modules
from stubber.publish.candidates import board_candidates, filter_list
from stubber.publish.defaults import GENERIC, GENERIC_L, default_board
from stubber.publish.pathnames import get_base, get_board_path, get_merged_path
from stubber.utils.config import CONFIG


def merge_all_docstubs(
    versions: Optional[Union[List[str], str]] = None,
    family: str = "micropython",
    ports: Optional[Union[List[str], str]] = None,
    boards: Optional[Union[List[str], str]] = None,
    # *,
    # mpy_path: Path = CONFIG.mpy_path,
):
    """merge docstubs and MCU stubs to merged stubs"""
    if versions is None:
        versions = [CONFIG.stable_version]
    if ports is None:
        ports = ["all"]
    if boards is None:
        boards = [GENERIC_L]
    if isinstance(versions, str):
        versions = [versions]
    if isinstance(ports, str):
        ports = [ports]
    if isinstance(boards, str):
        boards = [boards]

    candidates = list(board_candidates(versions=versions, family=family))
    candidates = filter_list(candidates, ports, boards)
    if not candidates:
        log.error("No candidates found")
        return

    log.info(f"checking {len(candidates)} possible board candidates")
    merged = 0
    for candidate in candidates:
        # use the default board for the port
        if candidate["board"] in GENERIC:
            candidate["board"] = default_board(
                port=candidate["port"], version=candidate["version"]
            )
        # check if we have MCU stubs of this version and port
        doc_path = CONFIG.stub_path / f"{get_base(candidate)}-docstubs"
        # src and dest paths
        board_path = get_board_path(candidate)
        merged_path = get_merged_path(candidate)

        # only continue if both folders exist
        if not doc_path.exists():
            log.warning(f"No docstubs found for {candidate['version']}")
            continue
        if not board_path.exists():
            log.debug(f"skipping {merged_path.name}, no MCU stubs found in {board_path}")
            continue
        log.info(f"Merge {candidate['version']} docstubs with boardstubs to {merged_path.name}")
        try:
            # TODO : webassembly: Need to merge from reference/pyscript as well 
            result = copy_and_merge_docstubs(board_path, merged_path, doc_path)
            if candidate["port"] == "webassembly":
                # TODO : webassembly: Need to merge from reference/pyscript as well 
                # use enrich_folder to merge the docstubs
                enrich_folder(
                    source_folder=CONFIG.mpy_stubs_path / "reference/pyscript",
                    target_folder=merged_path,
                    write_back=True,
                    copy_params=True,
                    copy_docstr=True,
                )
                pass
        except Exception as e:
            log.error(f"Error parsing {candidate['version']} docstubs: {e}")
            continue
        if result:
            merged += 1
    log.info(f"merged {merged} of {len(candidates)} candidates")
    return merged


def copy_and_merge_docstubs(fw_path: Path, dest_path: Path, docstub_path: Path):
    """
    Parameters:
        fw_path: Path to the source MCU stubs (absolute path)
        dest_path: Path to destination (absolute path)
        docstub_path: Path to docstubs


    Copy files from the firmware stub folders to the merged
    - 1 - Copy all MCU stubs to the package folder
    - 1.B - clean up a little bit
    - 2 - Enrich the MCU stubs with the document stubs

    """
    if dest_path.exists():
        # delete all files and folders from the destination
        shutil.rmtree(dest_path, ignore_errors=True)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
    try:
        log.debug(f"Copying MCU stubs from {fw_path}")
        shutil.copytree(fw_path, dest_path, symlinks=True, dirs_exist_ok=True)
    except OSError as e:
        log.error(f"Error copying stubs from : { fw_path}, {e}")
        raise (e)
    # rename the module.json file to firmware.json
    if (dest_path / "modules.json").exists():
        (dest_path / "modules.json").rename(dest_path / "firmware_stubs.json")

    # avoid duplicate modules : folder - file combinations
    # prefer folder from frozen stubs, over file from MCU stubs
    # No frozen here - OLD code ?
    for f in dest_path.glob("*"):
        if f.is_dir():
            for suffix in [".py", ".pyi"]:
                if (dest_path / f.name).with_suffix(suffix).exists():
                    (dest_path / f.name).with_suffix(suffix).unlink()

    # remove unwanted modules
    remove_modules(dest_path, RM_MERGED)
    # fixup the umodules
    recreate_umodules(dest_path)

    # 2 - Enrich the MCU stubs with the document stubs
    result = enrich_folder(
        source_folder=docstub_path,
        target_folder=dest_path,
        write_back=True,
        copy_params=True,
        copy_docstr=True,
    )

    refactor_rp2_module(dest_path)

    # copy the docstubs manifest.json file to the package folder
    if (docstub_path / "modules.json").exists():
        shutil.copy(docstub_path / "modules.json", dest_path / "doc_stubs.json")
    return result


def refactor_rp2_module(dest_path: Path):
    """refactor the rp2 module to allow for submodules"""
    rp2_file = dest_path / "rp2.pyi"
    if not rp2_file.exists():
        # not a rp2
        return

    log.info(f"refactor rps module stub")
    rp2_folder = dest_path / "rp2"
    rp2_folder.mkdir(exist_ok=True)
    if not (rp2_folder / "__init__.pyi").exists():
        # do not overwrite docstubs __init__.pyi
        rp2_file.rename(rp2_folder / "__init__.pyi")
    # copy the asm_pio.pyi file from the reference folder
    for submod in ["rp2/asm_pio.pyi"]:
        file = CONFIG.mpy_stubs_path / "reference/micropython" / submod
        if file.exists():
            shutil.copy(file, rp2_folder / file.name)
            log.info(f" - add rp2/{ file.name}")
