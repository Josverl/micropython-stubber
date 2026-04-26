"""
Merge firmware stubs and docstubs into a single folder.
"""

import shutil
from pathlib import Path
from typing import List, Optional, Union

import libcst as cst
from mpflash.logger import log
from stubber.codemod.enrich import enrich_folder
from stubber.merge_config import RM_MERGED, recreate_umodules, remove_modules
from stubber.publish.candidates import board_candidates, filter_list
from stubber.publish.defaults import GENERIC, GENERIC_L, default_board
from stubber.publish.pathnames import get_base, get_board_path, get_merged_path
from stubber.utils.config import CONFIG
from stubber.modcat import CP_REFERENCE_TO_DOCSTUB


def merge_all_docstubs(
    versions: Optional[Union[List[str], str]] = None,
    family: str = "micropython",
    ports: Optional[Union[List[str], str]] = None,
    boards: Optional[Union[List[str], str]] = None,
    clean: bool = True,
):
    """Merge docstubs and firmware stubs into merged stubs."""
    if versions is None:
        versions = [CONFIG.stable_version]
    if "stable" in versions:
        versions = [CONFIG.stable_version if v == "stable" else v for v in versions]
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
            candidate["board"] = default_board(port=candidate["port"], version=candidate["version"])
        # check if we have firmware stubs for this version and port
        doc_path = CONFIG.stub_path / f"{get_base(candidate)}-docstubs"
        # src and dest paths
        board_path = get_board_path(candidate)
        merged_path = get_merged_path(candidate)

        # only continue if both folders exist
        if not doc_path.exists():
            log.warning(f"No docstubs found for {candidate['version']}")
            continue
        if not board_path.exists():
            log.debug(f"skipping {merged_path.name}, no firmware stubs found in {board_path}")
            continue
        log.info(f"Merge {candidate['version']} docstubs with boardstubs to {merged_path.name}")
        try:
            # TODO : webassembly: Need to merge from reference/pyscript as well
            result = copy_and_merge_docstubs(board_path, merged_path, doc_path, clean=clean)
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


def copy_and_merge_docstubs(fw_path: Path, dest_path: Path, docstub_path: Path, clean: bool = True):
    """
    Parameters:
        fw_path: Path to the source firmware stubs (absolute path)
        dest_path: Path to destination (absolute path)
        docstub_path: Path to docstubs


    Copy files from the firmware stub folders to the merged
    - 1 - Copy all firmware stubs to the package folder
    - 1.B - clean up a little bit
    - 2 - Enrich the firmware stubs with the document stubs

    """
    if clean and dest_path.exists():
        # delete all files and folders from the destination
        shutil.rmtree(dest_path, ignore_errors=True)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
    try:
        log.debug(f"Copying firmware stubs from {fw_path}")
        shutil.copytree(fw_path, dest_path, symlinks=True, dirs_exist_ok=True)
    except OSError as e:
        log.error(f"Error copying stubs from : {fw_path}, {e}")
        raise (e)
    # rename the module.json file to firmware.json
    if (dest_path / "modules.json").exists():
        (dest_path / "modules.json").rename(dest_path / "firmware_stubs.json")

    # avoid duplicate modules : folder - file combinations
    # prefer folder from frozen stubs, over file from firmware stubs
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

    # 2 - Enrich the firmware stubs with the document stubs
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

    log.info("refactor rps module stub")
    rp2_folder = dest_path / "rp2"
    rp2_folder.mkdir(exist_ok=True)
    if not (rp2_folder / "__init__.pyi").exists():
        # do not overwrite docstubs __init__.pyi
        rp2_file.rename(rp2_folder / "__init__.pyi")
    log.info("copy the rp2/asm_pio files from the reference folder")
    for submod in [p for p in CP_REFERENCE_TO_DOCSTUB if p.startswith("rp2/asm")]:
        file = CONFIG.mpy_stubs_path / "reference/micropython" / submod
        if file.exists():
            log.info(f" - add rp2/{file.name}")
            shutil.copy(file, rp2_folder / file.name)
        else:
            log.warning(f" - rp2/{file.name} not found")

    patch_rp2_init_pyi(rp2_folder / "__init__.pyi")


def patch_rp2_init_pyi(rp2_init_file: Path) -> None:
    """
    Normalize generated rp2/__init__.pyi typing surface:
    - suppress `_PIO_ASM_Program: TypeAlias = Callable`
    - keep `PIOASMEmit` opaque (only __init__ + __getattr__)
    - make `_PIO_ASM_Program` an opaque class without `__getitem__`
    """
    if not rp2_init_file.exists():
        return

    source = rp2_init_file.read_text(encoding="utf-8")
    module = cst.parse_module(source)

    pioasmemit_replacement = cst.parse_statement(
        '''class PIOASMEmit:
    """
    Internal emitter used by the ``@asm_pio`` decorator. Not intended for
    direct use.

    PIO instructions, directives, and modifiers are exposed via
    :mod:`rp2.asm_pio` (which re-exports :mod:`rp2.asm_pio_rp2040`), and
    that module is the single source of truth for their typing surface.
    """
    def __init__(
        self,
        *,
        out_init: int | List | None = ...,
        set_init: int | List | None = ...,
        sideset_init: int | List | None = ...,
        side_pindir: bool = ...,
        in_shiftdir: int = ...,
        out_shiftdir: int = ...,
        autopush: bool = ...,
        autopull: bool = ...,
        push_thresh: int = ...,
        pull_thresh: int = ...,
        fifo_join: int = ...,
    ) -> None: ...
    def __getattr__(self, name: str) -> Incomplete: ...
'''
    )

    program_replacement = cst.parse_statement(
        '''class _PIO_ASM_Program:
    """Opaque handle representing an assembled PIO program.

    Returned by ``@asm_pio`` and consumed by ``StateMachine``/``PIO``.
    Users should not introspect or index this object. The chainable
    per-instruction expression that lives inside the decorator body is
    a different type (``rp2.asm_pio._PIOInstr``).
    """
'''
    )

    class RP2InitTransformer(cst.CSTTransformer):
        def __init__(self):
            self.changed = False
            self.found_pioasmemit = False
            self.found_program = False

        def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign):
            if (
                isinstance(updated_node.target, cst.Name)
                and updated_node.target.value == "_PIO_ASM_Program"
                and isinstance(updated_node.annotation.annotation, cst.Name)
                and updated_node.annotation.annotation.value == "TypeAlias"
                and isinstance(updated_node.value, cst.Name)
                and updated_node.value.value == "Callable"
            ):
                self.changed = True
                return cst.RemoveFromParent()
            return updated_node

        def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef):
            if updated_node.name.value == "PIOASMEmit":
                self.changed = True
                self.found_pioasmemit = True
                return pioasmemit_replacement
            if updated_node.name.value == "_PIO_ASM_Program":
                self.changed = True
                self.found_program = True
                return program_replacement
            return updated_node

    transformer = RP2InitTransformer()
    updated_module = module.visit(transformer)

    if not transformer.found_pioasmemit:
        log.warning(" - could not find class PIOASMEmit in rp2/__init__.pyi")
    if not transformer.found_program:
        log.warning(" - could not find class _PIO_ASM_Program in rp2/__init__.pyi")

    updated = updated_module.code
    if updated != source:
        rp2_init_file.write_text(updated, encoding="utf-8")
        log.info(" - patched rp2/__init__.pyi typing surface")
