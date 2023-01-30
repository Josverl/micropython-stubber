from collections import deque
from enum import Enum
from pathlib import Path
from typing import Iterator

PARTIALS_DIR = Path(__file__).parent.absolute()

PARTIAL_START = "###PARTIAL###"
PARTIAL_END = "###PARTIALEND###"


def _read_partial(path: Path) -> Iterator[str]:
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
    DB_ENTRY = "db_entry"

    @property
    def partial_path(self) -> Path:
        return (PARTIALS_DIR / self.value).with_suffix(".py")

    def contents(self) -> str:
        return "".join(_read_partial(self.partial_path))


__all__ = ["Partial"]
