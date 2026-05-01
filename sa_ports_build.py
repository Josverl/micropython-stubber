# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "mpbuild@git+https://github.com/josverl/mpbuild@build_sa_ports",
#   "mpflash"
# ]
# ///

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import mpbuild.build as mpb  # type: ignore
import mpflash.basicgit as git
from mpbuild.board_database import Board, Database  # type: ignore
from mpflash.config import config as mpflash_config
from mpflash.custom import add_custom_firmware
from mpflash.versions import get_preview_mp_version, get_stable_mp_version
import mpflash.db.core  # noqa: F401  # initializes the peewee database connection
from typing_extensions import Tuple

ROOT = Path("~/combo/micropython-stubs").expanduser().resolve()

def _wsl_windows_home() -> Path | None:
    """Return the Windows user home as a WSL path, or None if not running under WSL."""
    if not os.environ.get("WSL_DISTRO_NAME"):
        return None
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        try:
            result = subprocess.run(["wslpath", "-u", userprofile], capture_output=True, text=True)
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except FileNotFoundError:
            pass
    return None



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
    fw_name = {
        "webassembly": "micropython.*",
        "unix": "micropython",
        "windows": "micropython.exe",
    }.get(board.port.name, "firmware.*")
    # create the destination directory
    if board.port.name in {"unix", "windows"}:
        # just a single file
        add_custom_firmware(
            fw_path=build_dir / fw_name,
            force=True,
            description="Stand Alone build using mpbuild",
            custom=True,
        )
    elif board.port.name == "webassembly":
        # all webassembly binaries need to be in a single folder
        # Create a zip file with the firmware files
        zip_name = f"{board.name}-{variant}-{version}"
        zip_path = build_dir / zip_name
        # Create a zip file with only the micropython.mjs and micropython.wasm files
        import zipfile

        with zipfile.ZipFile(zip_path.with_suffix(".zip"), "w") as zf:
            for pattern in ["micropython.mjs", "micropython.wasm"]:
                for file in build_dir.glob(pattern):
                    zf.write(file, arcname=file.name)
        add_custom_firmware(
            fw_path=zip_path.with_suffix(".zip"),
            force=True,
            description="Built using mpbuild",
            custom=True,
        )


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
    # for unix ports - mark the firmware as executable
    if _board.port.name in {"unix"}:
        for fw_file in fw_path.glob("micropython*"):
            fw_file.chmod(fw_file.stat().st_mode | 0o111)
    copy_firmware(fw_path=fw_path, board=_board, variant=variant, version=version, build=build_nr, mpy_dir=mpy_dir)
    return True


def main():
    # Save the firmwares in the Windows downloads folder when running under WSL
    if windows_home := _wsl_windows_home():
        mpflash_config.firmware_folder = windows_home / "Downloads/firmware"
        print(f"Running under WSL, saving firmware to Windows Downloads folder: {mpflash_config.firmware_folder}")

    mpy_dir = ROOT / "repos/micropython"
    mpy_dir = mpy_dir.resolve().absolute()
    assert mpy_dir.exists(), f"Micropython repo not found in {mpy_dir}"

    builds = [
        # ( port , [variant], [extra args])
        ("unix", "standard"),
        # ("windows", "standard"),
        # ("windows", "dev"),
        # ("webassembly", "standard"),
        # ("webassembly", "pyscript"),
        # ("webassembly", "pyscript", 'JSFLAGS+="-s NODERAWFS=1"'),
    ]

    versions = [
        # "v1.23.0",
        "v1.24.0",
        # "v1.24.1",
        # "v1.25.0",
        # "v1.26.0",
        "v1.26.1",
        "v1.27.0",
        get_stable_mp_version(),
        get_preview_mp_version(),
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
# uv pip install git+https://github.com/josverl/mpbuild@sa_build
if __name__ == "__main__":
    main()
