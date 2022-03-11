import logging

from fnmatch import fnmatch
from pathlib import Path

from typing import List, Optional

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

def read_exclusion_file(path: Optional[Path] = None) -> List[str]:
    """Read a .exclusion file to determine which files should not be automatically re-generated
    in .GitIgnore format

    """
    if path is None:
        path = Path(".")
    try:
        with open(path.joinpath(".exclusions")) as f:
            content = f.readlines()
            return [line.rstrip() for line in content if line[0] != "#" and len(line.strip()) != 0]
    except OSError:
        return []
    # exclusions = read_exclusion_file()


def should_ignore(file: str, exclusions: List[str]) -> bool:
    """Check if  a file matches a line in the exclusion list."""
    for excl in exclusions:
        if fnmatch(file, excl):
            return True
    return False
    # for file in Path(".").glob("**/*.py*"):
    #     if should_ignore(str(file), exclusions):
    #         print(file)
