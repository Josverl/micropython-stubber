# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "micropython-stubber",
#   "mpflash",
#   "click",
#   "poetry"
# ]
# ///
# Run createstubs for stand-alone MicroPython ports (unix, windows).
# Firmware must already be built and registered with mpflash (see sa_ports_build.py).
# webassembly support to be added later.

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

import click
import importlib.resources
from mpflash.config import config as mpflash_config
from mpflash.downloaded import find_downloaded_firmware
from mpflash.logger import set_loglevel
from mpflash.versions import get_preview_mp_version, get_stable_mp_version
import mpflash.db.core  # noqa: F401  # initializes the peewee database connection

set_loglevel("TRACE")

CREATESTUBS_PY = importlib.resources.files("stubber.board").joinpath("createstubs.py")


def _find_stubs_root() -> Path | None:
    """Return the micropython-stubs root relative to cwd, or None if not found."""
    cwd = Path.cwd()
    if cwd.name == "micropython-stubs":
        return cwd
    candidate = cwd / "micropython-stubs"
    if candidate.is_dir():
        return candidate
    return None


def get_sa_firmware_path(board_id: str, version: str) -> Path | None:
    """Find a registered custom firmware file for the given board_id and version."""
    from mpflash.db.models import Firmware
    print(f"  firmware_folder : {mpflash_config.firmware_folder}")
    print(f"  db_path         : {mpflash_config.db_path}")
    # Show all custom firmware records in the db for context
    all_custom = list(Firmware.select().where(Firmware.custom == True))
    print(f"  all custom firmware records in db: {len(all_custom)}")
    for fw in all_custom:
        print(f"    board_id={fw.board_id!r}  version={fw.version!r}  file={fw.firmware_file!r}  custom_id={fw.custom_id!r}")
    fws = find_downloaded_firmware(
        board_id=board_id,
        custom=True,
        version=version,
    )
    for fw in fws:
        fw_path = mpflash_config.firmware_folder / str(fw.firmware_file)
        print(f"  checking        : {fw_path} exists={fw_path.exists()}")
        if fw_path.exists():
            return fw_path
    return None


def run_createstubs(port: str, version: str, variant: str, dest: Path) -> bool:
    """Run createstubs.py with the stand-alone firmware for the given port/version."""
    board_id = f"{port}-{variant}"
    firmware_path = get_sa_firmware_path(board_id, version)
    if firmware_path is None:
        print(f"No firmware found for {board_id} {version}. Run sa_ports_build.py first.")
        return False

    print(f"Using firmware: {firmware_path}")

    if platform.system() == "Linux":
        # ensure executable
        firmware_path.chmod(firmware_path.stat().st_mode | 0o111)
        result = subprocess.run([str(firmware_path), str(CREATESTUBS_PY), "--path", str(dest)])
    elif platform.system() == "Windows":
        result = subprocess.run([str(firmware_path), str(CREATESTUBS_PY), "--path", str(dest)])
    else:
        print(f"Unsupported platform: {platform.system()}")
        return False

    return result.returncode == 0


def run_stubber(cmd: str, version: str, port: str, cwd: Path) -> bool:
    """Run a stubber sub-command for the given version and port, from cwd."""
    result = subprocess.run(["stubber", cmd, "--version", version, "--port", port], cwd=str(cwd))
    return result.returncode == 0


@click.command()
@click.argument("port", type=click.Choice(["unix", "windows"], case_sensitive=False))
@click.option("--variant", "-v", default="standard", show_default=True, help="Firmware variant.")
@click.option("--version", default=None, help="MicroPython version tag, 'stable', or 'preview' (default: stable).")
@click.option(
    "--stubs-root",
    default=None,
    show_default=False,
    type=click.Path(file_okay=False),
    help="Root of the micropython-stubs repo. Defaults to cwd or './micropython-stubs' if present.",
)
@click.option(
    "--dest",
    default=None,
    type=click.Path(),
    help="Destination path for stubs output (default: stubs-root).",
)
@click.option("--merge/--no-merge", default=True, show_default=True, help="Run stubber merge after createstubs.")
@click.option("--build/--no-build", default=True, show_default=True, help="Run stubber build after merge.")
@click.option("--publish/--no-publish", default=False, show_default=True, help="Publish the package to PyPI after build.")
def main(port: str, variant: str, version: str | None, stubs_root: str, dest: str | None, merge: bool, build: bool, publish: bool):
    """Run createstubs for a stand-alone MicroPython PORT and process the output."""
    # mpflash resolves firmware_folder from MPFLASH_FIRMWARE env var or platform default.
    # Set MPFLASH_FIRMWARE in your shell to override (e.g. on WSL pointing to Windows Downloads).
    print(f"Firmware folder: {mpflash_config.firmware_folder}")

    if version is None or version == "stable":
        version = get_stable_mp_version()
        print(f"Using stable version: {version}")
    elif version == "preview":
        version = get_preview_mp_version()
        print(f"Using preview version: {version}")

    if stubs_root is None:
        resolved = _find_stubs_root()
        if resolved is None:
            raise click.UsageError(
                "Cannot determine stubs root. Run from inside 'micropython-stubs', "
                "from a folder containing 'micropython-stubs', or pass --stubs-root."
            )
        stubs_root = str(resolved)

    stubs_root_path = Path(stubs_root).expanduser().resolve()
    dest_path = Path(dest).expanduser().resolve() if dest else stubs_root_path
    dest_path.mkdir(parents=True, exist_ok=True)

    print(f"Stubs root   : {stubs_root_path}")
    print(f"Stubs dest   : {dest_path}")
    print(f"Running createstubs for {port}-{variant} {version}")
    if not run_createstubs(port=port, version=version, variant=variant, dest=dest_path):
        print(f"createstubs failed for {port} {version}")
        raise SystemExit(1)

    if merge:
        print(f"Running stubber merge for {port} {version} (cwd={stubs_root_path})")
        if not run_stubber("merge", version=version, port=port, cwd=stubs_root_path):
            print(f"stubber merge failed for {port} {version}")
            raise SystemExit(1)

    if build:
        print(f"Running stubber build for {port} {version} (cwd={stubs_root_path})")
        if not run_stubber("build", version=version, port=port, cwd=stubs_root_path):
            print(f"stubber build failed for {port} {version}")
            raise SystemExit(1)

    if publish:
        print(f"Publishing stubs for {port} {version} (cwd={stubs_root_path})")
        result = subprocess.run(["stubber", "publish", "--version", version, "--port", port, "--pypi"], cwd=str(stubs_root_path))
        if result.returncode != 0:
            print(f"stubber publish failed for {port} {version}")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
