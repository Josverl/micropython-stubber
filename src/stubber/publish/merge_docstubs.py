""" Merge firmware stubs and docstubs into a single folder
"""

import shutil
from pathlib import Path

from loguru import logger as log

from stubber.codemod.enrich import enrich_folder
from stubber.publish.candidates import firmware_candidates
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

LAST_VERSION = "v1.19.1"

def merge_all_docstubs(versions, family: str = "micropython", *, mpy_path=CONFIG.mpy_path):
    """merge docstubs into firmware stubs"""
    for fw in firmware_candidates(versions=versions, family=family ):
        # check if we have firmware stubs of this version and port
        base = f"{fw['family']}-{clean_version(fw['version'],flat=True)}"
        if fw["board"] == "":
            fw_folder = f"{base}-{fw['port']}"
            mrg_folder = fw_folder + "-merged"
            doc_folder = f"{base}-docstubs"
        else:
            fw_folder = f"{base}-{fw['port']}-{fw['board']}"
            mrg_folder = fw_folder + "-merged"
            doc_folder = f"{base}-docstubs"

        fw_path = CONFIG.stub_path / fw_folder
        mrg_path = CONFIG.stub_path / mrg_folder
        doc_path = CONFIG.stub_path / doc_folder

        if not fw_path.exists():
            if fw["version"] != 'latest':
                # only continue if both folders exist
                log.debug(f"skipping {mrg_folder}, no firmware stubs found")
                continue
            else:
                # try to get the fw_path from the last released version
                base = f"{fw['family']}-{clean_version(LAST_VERSION,flat=True)}"
                if fw["board"] == "":
                    fw_folder = f"{base}-{fw['port']}"
                else:
                    fw_folder = f"{base}-{fw['port']}-{fw['board']}"
                fw_path = CONFIG.stub_path / fw_folder
                # check again
                if not fw_path.exists():
                    # only continue if both folders exist
                    log.debug(f"skipping {mrg_folder}, no firmware stubs found")
                    continue

            
        if not doc_path.exists():
            print(f"Warning: no docstubs for {fw['version']}")
        log.info(f"Merge docstubs for {fw['family']} {fw['version']} {fw['port']} {fw['board']}")
        copy_docstubs(fw_path, mrg_path, doc_path)


def copy_docstubs(fw_path: Path, dest_path: Path, docstub_path: Path):
    """
    Parameters:
        fw_path: Path to firmware stubs (absolute path)
        dest_path: Path to destination (absolute path)
        mpy_version: micropython version ('1.18')

    Copy files from the firmware stub folders to the merged
    - 1 - Copy all firmware stubs to the package folder
    - 1.B - clean up a little bit
    - 2 - Enrich the firmware stubs with the document stubs

    """
    if dest_path.exists():
        # delete all files and folders from the destination
        shutil.rmtree(dest_path, ignore_errors=True)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
    try:
        log.trace(f"Copying firmware stubs from {fw_path}")
        shutil.copytree(fw_path, dest_path, symlinks=True, dirs_exist_ok=True)
    except OSError as e:
        log.error(f"Error copying stubs from : { fw_path}, {e}")
        raise (e)
    # rename the module.json file to firmware.json
    if (dest_path / "modules.json").exists():
        (dest_path / "modules.json").rename(dest_path / "firmware_stubs.json")


    # avoid duplicate modules : folder - file combinations
    # prefer folder from frozen stubs, over file from firmware stubs
    for f in dest_path.glob("*"):
        if f.is_dir():
            for suffix in [".py", ".pyi"]:
                if (dest_path / f.name).with_suffix(suffix).exists():
                    (dest_path / f.name).with_suffix(suffix).unlink()

    # delete buitins.pyi in the package folder
    for name in [
        "builtins",  # creates conflicts, better removed
        "pycopy_imphook",  # is not intended to be used directly, and has an unresolved subclass
    ]:
        for suffix in [".py", ".pyi"]:
            if (dest_path / name).with_suffix(suffix).exists():
                (dest_path / name).with_suffix(suffix).unlink()

    # 2 - Enrich the firmware stubs with the document stubs
    result = enrich_folder(dest_path, docstub_path=docstub_path, write_back=True)

    # copy the docstubs manifest.json file to the package folder
    # if (docstub_path / "modules.json").exists():
    shutil.copy(docstub_path / "modules.json", dest_path / "doc_stubs.json")
    return result
