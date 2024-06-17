from collections import deque
from enum import Enum
from pathlib import Path
from typing import Iterator, cast

PARTIALS_DIR = Path(__file__).parent.absolute()

PARTIAL_START = "###PARTIAL###"
PARTIAL_END = "###PARTIALEND###"


def _read_partial(path: Path) -> Iterator[str]:
    """
    Read a partial from the file at `path`
    and yield only the lines between the ###PARTIAL### and ###PARTIALEND### markers
    """
    lines = deque(path.read_text(encoding="utf-8").splitlines(keepends=True))
    _start = False
    _end = False
    while True:
        try:
            if not _start and (line := lines.popleft()):
                _start = line.strip() == PARTIAL_START
            if not _end and (line := lines.pop()):
                _end = line.strip() == PARTIAL_END
            if _start and _end:
                break
        except IndexError:
            # or avoid erroring out if the file does not have the markers
            raise ValueError(f"Partial {path} does not have ###PARTIAL### and ###PARTIALEND### markers")

    yield from lines


class _PartialMember:
    def contents(self) -> str:
        """Return the contents of the partial."""
        return "".join(_read_partial(cast(Enum, self).value))


Partial = Enum(
    "Partial",
    [(p.stem.upper(), p.absolute()) for p in PARTIALS_DIR.glob("*.py")],
    type=_PartialMember,
)


__all__ = ["Partial"]
