from collections import deque
from enum import Enum
from pathlib import Path
from typing import Iterator

# TODO: this way of accessing the partials is not very robust
PARTIALS_DIR = Path(__file__).parent.absolute()

PARTIAL_START = "###PARTIAL###"
PARTIAL_END = "###PARTIALEND###"


def _read_partial(path: Path) -> Iterator[str]:
    """
    Read a partial from the file at `path`
    and yield only the lines between the ###PARTIAL### and ###PARTIALEND### markers
    """
    lines = deque(path.read_text().splitlines(keepends=True))
    _start = False
    _end = False
    while True:
        if not _start and (line := lines.popleft()):
            _start = line.strip() == PARTIAL_START
        if not _end and (line := lines.pop()):
            _end = line.strip() == PARTIAL_END
        if _start and _end:
            break
    yield from lines


class Partial(Enum):
    DB_MAIN = "db_main"
    LVGL_MAIN = "lvgl_main"

    @property
    def partial_path(self) -> Path:
        # TODO: this way of accessing the partials is not very robust
        return (PARTIALS_DIR / self.value).with_suffix(".py")

    def contents(self) -> str:
        """Return the contents of the partial"""	
        return "".join(_read_partial(self.partial_path))


__all__ = ["Partial"]
