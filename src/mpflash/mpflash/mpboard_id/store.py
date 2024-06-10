import functools
import zipfile
from pathlib import Path
from typing import List, Optional

import jsons

from mpflash.mpboard_id.board import Board

###############################################################################################
HERE = Path(__file__).parent
###############################################################################################


def write_boardinfo_json(board_list: List[Board], *, folder: Path):
    """Writes the board information to a JSON file.

    Args:
        board_list (List[Board]): The list of Board objects.
        folder (Path): The folder where the compressed JSON file will be saved.
    """
    import zipfile

    # create a zip file with the json file
    with zipfile.ZipFile(folder / "board_info.zip", "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        # write the list to json file inside the zip
        with zipf.open("board_info.json", "w") as fp:
            fp.write(jsons.dumps(board_list, jdkwargs={"indent": 4}).encode())


@functools.lru_cache(maxsize=20)
def read_known_boardinfo(board_info: Optional[Path] = None) -> List[Board]:

    if not board_info:
        board_info = HERE / "board_info.zip"
    if not board_info.exists():
        raise FileNotFoundError(f"Board info file not found: {board_info}")

    with zipfile.ZipFile(board_info, "r") as zf:
        with zf.open("board_info.json", "r") as file:
            info = jsons.loads(file.read().decode(encoding="utf-8"), List[Board])

    return info
