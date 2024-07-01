import shutil
from pathlib import Path
from typing import Union

import jsonlines
import requests
from loguru import logger as log

# re-use logic from mpremote
from mpremote.mip import _rewrite_url as rewrite_url  # type: ignore

from mpflash.common import FWInfo
from mpflash.config import config
from mpflash.versions import get_preview_mp_version, get_stable_mp_version


def add_firmware(
    source: Union[Path, str],
    new_fw: FWInfo,
    *,
    force: bool = False,
    custom: bool = False,
    description: str = "",
) -> bool:
    """Add a firmware to the firmware folder.

    stored in the port folder, with the same filename as the source.

    """
    # Check minimal info needed
    if not new_fw.port or not new_fw.board:
        log.error("Port and board are required")
        return False
    if not isinstance(source, Path) and not source.startswith("http"):
        log.error(f"Invalid source {source}")
        return False

    # use sensible defaults
    source_2 = Path(source)
    new_fw.ext = new_fw.ext or source_2.suffix
    new_fw.variant = new_fw.variant or new_fw.board
    new_fw.custom = new_fw.custom or custom
    new_fw.description = new_fw.description or description
    if not new_fw.version:
        # TODO: Get version from filename
        # or use the last preview version
        new_fw.version = get_preview_mp_version() if new_fw.preview else get_stable_mp_version()

    config.firmware_folder.mkdir(exist_ok=True)

    fw_filename = config.firmware_folder / new_fw.port / source_2.name

    new_fw.filename = str(fw_filename.relative_to(config.firmware_folder))
    new_fw.firmware = source.as_uri() if isinstance(source, Path) else source

    if not copy_firmware(source, fw_filename, force):
        log.error(f"Failed to copy {source} to {fw_filename}")
        return False
    # add to inventory
    with jsonlines.open(config.firmware_folder / "firmware.jsonl", "a") as writer:
        log.info(f"Adding {new_fw.port} {new_fw.board}")
        log.info(f"    to {fw_filename}")

        writer.write(new_fw.to_dict())
    return True


def copy_firmware(source: Union[Path, str], fw_filename: Path, force: bool = False):
    """Add a firmware to the firmware folder.
    stored in the port folder, with the same filename as the source.
    """
    if fw_filename.exists() and not force:
        log.error(f" {fw_filename} already exists. Use --force to overwrite")
        return False
    fw_filename.parent.mkdir(exist_ok=True)
    if isinstance(source, Path):
        if not source.exists():
            log.error(f"File {source} does not exist")
            return False
        # file copy
        log.debug(f"Copy {source} to {fw_filename}")
        shutil.copy(source, fw_filename)
        return True
    # handle github urls
    url = rewrite_url(source)
    if str(source).startswith("http://") or str(source).startswith("https://"):
        log.debug(f"Download {url} to {fw_filename}")
        response = requests.get(url)

        if response.status_code == 200:
            with open(fw_filename, "wb") as file:
                file.write(response.content)
                log.info("File downloaded and saved successfully.")
                return True
        else:
            print("Failed to download the file.")
            return False
    return False
