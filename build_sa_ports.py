from __future__ import annotations

import time
from pathlib import Path

import jsonlines
import mpbuild.build as mpb
from mpbuild import board_database
from mpbuild.board_database import Board, Database
from typing_extensions import List, Tuple

import mpflash.basicgit as git
from mpflash.common import FWInfo
from mpflash.versions import (clean_version, get_preview_mp_version,
                              get_stable_mp_version, micropython_versions)


def copy_firmware(board:Board, variant:str|None, version:str, build: str, mpy_dir:Path, fw_path:Path ):
    """Copy the built firmware to the destination directory."""
    # find the build directory
    if board.physical_board:
        # all other ports
        if variant:
            build_dir = mpy_dir / f"ports/{board.port.name}/build-{board.name}-{variant}"
        else:
            build_dir = mpy_dir / f"ports/{board.port.name}/build-{board.name}"
    else:
        build_dir = mpy_dir / f"ports/{board.port.name}/build-{variant}"
    # what is the resulting name of the firmware files?
    fw_name = {
        "webassembly": "micropython.*",
        "unix": "micropython",
        "windows": "micropython.exe"
    }.get(board.port.name, "firmware.*")
    # create the destination directory
    
    port_path = fw_path / board.port.name
    port_path.mkdir(parents=True, exist_ok=True)


    for file in build_dir.glob(fw_name):
        if file.suffix in {".map", ".dis"}:
            # skip these extensions
            continue
        elif len(file.suffix) > 1:
            dest_name = f"{board.name}-{variant}-{version}{file.suffix}"
        else:
            dest_name = f"{board.name}-{variant}-{version}"
        # normalize the names 
        dest_name = dest_name.replace("-standard", "")
        dest_file = port_path / dest_name
        dest_file.write_bytes(file.read_bytes())

        fw = FWInfo(
            port=board.port.name,
            board=board.name,
            variant=variant or "",
            version=version,
            preview="-preview" in version,
            build=build,
            ext=file.suffix,
            custom=False,
            description="Built using mpbuild",
            filename=str(dest_file.relative_to(port_path)),
        )
        # add to inventory
        with jsonlines.open(fw_path / "firmware.jsonl", "a") as writer:
            print(f"Adding {fw.port} {fw.board}")
            print(f"    to {fw.filename}")
            writer.write(fw.to_dict())





def build_sa_ports( builds:List[Tuple],versions:List[str], mpy_dir:Path, fw_path:Path):
    """Build all ports for the stand alone boards."""
    for version in versions:
        print("=" * 60)
        build_nr = ""
        if "preview" in version:
            ok = git.checkout_tag("master", mpy_dir)
            if describe := git.get_git_describe(mpy_dir):
                parts = describe.split("-", 3)
                if len( parts) >=3:
                    build_nr = parts[2]
        else:
            ok = git.checkout_tag(version, mpy_dir)
        if not ok:
            print(f"Failed to checkout {version} in {mpy_dir}")
            continue
        
        print( git.get_git_describe(mpy_dir))
        # un-cached database 
        db = Database(mpy_dir)
        print (f"boards found {len(db.boards.keys())}")


        print(f"Building {version} , build {build_nr}")
        print("=" * 60)
        for build in builds:
            if len(build) == 1:
                board, variant, extras = build[0], None, []
            elif len(build) == 2:
                board, variant, extras = build[0], build[1], []
            else:
                board, variant, extras = build
                if isinstance(extras, str):
                    extras = extras.split(' ')

            if board not in db.boards.keys():
                print(f"Board '{board}' not found for version '{version}'")
                continue

            # resolve boardname
            _board = db.boards[board]

            # if variant is not None:
            #     _variant = _board.find_variant(variant)
            #     if _variant is None:
            #         print(f"Invalid variant '{variant}'")
            #         raise SystemExit()
            if variant == "":
                variant = None
            try: 
                mpb.clean_board(board = _board.name, variant = variant, mpy_dir = mpy_dir) # type: ignore
                mpb.build_board( board = _board.name, variant = variant, mpy_dir = mpy_dir, extra_args= extras) 
                # make_mpy_cross = False 
            except SystemExit as e:
                print(f"Failed to build {board} {variant} {version}: {e}")
                continue
            copy_firmware( fw_path= fw_path, board=_board, variant=variant, version=version, build=build_nr, mpy_dir=mpy_dir)

def main():
    mpy_dir = Path("/home/jos/micropython") 
    assert mpy_dir.exists()
    build_sa_ports(
        builds = [
            # ("windows", "standard"),
            # ("unix", "standard"),
            # ("webassembly", "standard", "-lnodefs.js"),
            ("webassembly", "pyscript",  "-lnodefs.js"),
            # ("WEACT_F411_BLACKPILL", "V20_FLASH_4M"),
            # ("RPI_PICO2_W",),
            ],
        versions = [
            get_stable_mp_version(), 
            get_preview_mp_version(), 
            # "preview",
                    ],
        mpy_dir = mpy_dir,
        fw_path = Path(f"./firmware")
        )

if __name__ == "__main__":
    main()