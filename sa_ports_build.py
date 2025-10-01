from __future__ import annotations

import time
from pathlib import Path

import jsonlines
import mpbuild.build as mpb  # type: ignore
import mpflash.basicgit as git
from mpbuild.board_database import Board, Database  # type: ignore
from mpflash.versions import get_preview_mp_version, get_stable_mp_version
from typing_extensions import Tuple


def copy_firmware(board: Board, variant: str | None, version: str, build: str, mpy_dir: Path, fw_path: Path):
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
    fw_name = {"webassembly": "micropython.*", "unix": "micropython", "windows": "micropython.exe"}.get(board.port.name, "firmware.*")
    # create the destination directory

    port_path = fw_path / board.port.name
    if board.port.name == "webassembly":
        # all webassembly binaries need to be in a single folder
        port_path = fw_path / f"{board.port.name}/{board.name}-{variant}-{version}"

    port_path.mkdir(parents=True, exist_ok=True)

    for file in build_dir.glob(fw_name):
        if file.suffix in {".map", ".dis"}:
            # skip these extensions
            continue
        elif board.port.name == "webassembly":
            # unchanged name, all in shared folder per version
            dest_name = file.name
        elif len(file.suffix) > 1:
            dest_name = f"{board.name}-{variant}-{version}{file.suffix}"
        else:
            dest_name = f"{board.name}-{variant}-{version}"
        # normalize the names
        dest_name = dest_name.replace("-standard", "")
        dest_file = port_path / dest_name
        dest_file.write_bytes(file.read_bytes())

        # FIXME: should use mpflash.db to add to the database instead of this ad-hoc method
        fw = {
            "port": board.port.name,
            "board": board.name,
            "variant": variant or "",
            "version": version,
            "preview": "-preview" in version,
            "build": build,
            "ext": file.suffix,
            "custom": False,
            "description": "Built using mpbuild",
            "filename": str(dest_file.relative_to(port_path)),
        }
        # add to inventory
        with jsonlines.open(fw_path / "firmware.jsonl", "a") as writer:
            print(f"Adding {fw['port']} {fw['board']}")
            print(f"    to {fw['filename']}")
            writer.write(fw)


def build_sa_port(build: Tuple, version: str, mpy_dir: Path, fw_path: Path):
    """Build a single port for a stand alone board."""
    print("=" * 60)
    build_nr = ""
    if "preview" in version:
        ok = git.checkout_tag("master", mpy_dir)
        if describe := git.get_git_describe(mpy_dir):
            parts = describe.split("-", 3)
            if len(parts) >= 3:
                build_nr = parts[2]
    else:
        ok = git.checkout_tag(version, mpy_dir)
    if not ok:
        print(f"Failed to checkout {version} in {mpy_dir}")
        return False

    print(git.get_git_describe(mpy_dir))
    # un-cached database
    db = Database(mpy_dir)
    print(f"boards found {len(db.boards.keys())}")

    print(f"Building {version}, build {build_nr}")
    print("=" * 60)

    if len(build) == 1:
        board, variant, extras = build[0], None, []
    elif len(build) == 2:
        board, variant, extras = build[0], build[1], []
    else:
        board, variant, extras = build
        if isinstance(extras, str):
            extras = extras.split(" ")

    if board not in db.boards.keys():
        print(f"Board '{board}' not found for version '{version}'")
        return False

    # resolve boardname
    _board = db.boards[board]

    if variant == "":
        variant = None

    try:
        mpb.clean_board(board=_board.name, variant=variant, mpy_dir=str(mpy_dir))
        mpb.build_board(board=_board.name, variant=variant, mpy_dir=mpy_dir, extra_args=extras)
    except SystemExit as e:
        print(f"Failed to build {board} {variant} {version}: {e}")
        return False

    copy_firmware(fw_path=fw_path, board=_board, variant=variant, version=version, build=build_nr, mpy_dir=mpy_dir)
    return True


def main():
    mpy_dir = Path("./repos/micropython").resolve().absolute()
    assert mpy_dir.exists()

    builds = [
        # ( port , [variant], [extra args])
        ("unix", "standard"),
        ("windows", "standard"),
        ("webassembly", "standard"),
        ("webassembly", "pyscript"),
        # ("webassembly", "pyscript", 'JSFLAGS+="-s NODERAWFS=1"'),
    ]

    versions = [
        # "v1.25.0",
        # "v1.26.0",
        get_stable_mp_version(),
        # get_preview_mp_version(),
    ]
    # TODO: Use the same path as mpflash
    fw_path = Path("./firmware")

    for version in versions:
        for build in builds:
            success = build_sa_port(
                build=build,
                version=version,
                mpy_dir=mpy_dir,
                fw_path=fw_path,
            )
            if not success:
                print(f"Build failed for {build} {version}")


# requires MPBuild PR70 to build webassemby and windows versions using mpbuild
# https://github.com/mattytrentini/mpbuild/pull/70
if __name__ == "__main__":
    main()
