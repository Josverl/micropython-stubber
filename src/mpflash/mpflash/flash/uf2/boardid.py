from pathlib import Path

from loguru import logger as log


def get_board_id(path: Path):
    # Option : read Board-ID from INFO_UF2.TXT
    board_id = "Unknown"
    with open(path / "INFO_UF2.TXT") as f:
        data = f.readlines()
    for line in data:
        if line.startswith("Board-ID"):
            board_id = line[9:].strip()
    log.debug(f"INFO_UF2.TXT Board-ID={board_id}")
    return board_id
