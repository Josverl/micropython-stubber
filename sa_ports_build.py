# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "mpbuild@git+https://github.com/josverl/mpbuild@build_sa_ports",
#   "mpflash",
#   "click"
# ]
# ///
# requires MPBuild PR70 to build webassemby and windows versions using mpbuild

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

import click
import mpbuild.build as mpb  # type: ignore
import mpflash.basicgit as git
from mpbuild.board_database import Board, Database  # type: ignore
from mpflash.config import config as mpflash_config
from mpflash.custom import add_custom_firmware
from mpflash.versions import get_preview_mp_version, get_stable_mp_version
import mpflash.db.core  # noqa: F401  # initializes the peewee database connection

ROOT = Path("~/combo/micropython-stubs").expanduser().resolve()


def copy_firmware(board: Board, variant: str | None, version: str, build: str, mpy_dir: Path, fw_path: Path, register: bool = True):
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
        if register:
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
        # add to mpflash list of custom firmwares
        if register:
            add_custom_firmware(
                fw_path=zip_path.with_suffix(".zip"),
                force=True,
                description="Built using mpbuild",
                custom=True,
            )


def build_sa_port(
    port: str,
    version: str,
    mpy_dir: Path,
    fw_path: Path,
    variant: str | None = None,
    extras: list[str] | None = None,
    register: bool = True,
):
    """Build a single stand-alone port."""
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

    if port not in db.boards.keys():
        print(f"Board '{port}' not found for version '{version}'")
        return False

    _board = db.boards[port]
    if not variant:
        variant = None

    try:
        mpb.clean_board(board=_board.name, variant=variant, mpy_dir=str(mpy_dir))
        mpb.build_board(board=_board.name, variant=variant, mpy_dir=mpy_dir, extra_args=extras or [])
    except SystemExit as e:
        print(f"Failed to build {port} {variant} {version}: {e}")
        return False
    # for unix ports - mark the firmware as executable
    if _board.port.name in {"unix"}:
        for fw_file in fw_path.glob("micropython*"):
            fw_file.chmod(fw_file.stat().st_mode | 0o111)
    copy_firmware(fw_path=fw_path, board=_board, variant=variant, version=version, build=build_nr, mpy_dir=mpy_dir, register=register)
    return True


@click.command()
@click.argument("port")
@click.option("--variant", "-v", default="standard", show_default=True, help="Build variant.")
@click.option("--version", default=None, help="MicroPython version tag (default: stable).")
@click.option("--extra", "-e", default="", show_default=True, help="Extra build arguments.")
@click.option("--fw-path", default="./firmware", show_default=True, type=click.Path(), help="Destination folder for firmware files.")
@click.option("--register/--no-register", default=True, show_default=True, help="Register the firmware with mpflash after building.")
def main(port: str, variant: str, version: str | None, extra: str, fw_path: str, register: bool):
    """Build a stand-alone MicroPython binary for PORT and register it with mpflash."""
    # mpflash resolves firmware_folder from MPFLASH_FIRMWARE env var or platform default.
    # Set MPFLASH_FIRMWARE in your shell to override (e.g. on WSL pointing to Windows Downloads).
    print(f"Firmware folder: {mpflash_config.firmware_folder}")

    if version is None or version == "stable":
        version = get_stable_mp_version()
        print(f"Using stable version: {version}")
    elif version == "preview":
        version = get_preview_mp_version()
        print(f"Using preview version: {version}")

    mpy_dir = ROOT / "repos/micropython"
    mpy_dir = mpy_dir.resolve().absolute()
    assert mpy_dir.exists(), f"Micropython repo not found in {mpy_dir}"

    extras = extra.split() if extra else []

    success = build_sa_port(
        port=port,
        version=version,
        mpy_dir=mpy_dir,
        fw_path=Path(fw_path),
        variant=variant or None,
        extras=extras,
        register=register,
    )
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
