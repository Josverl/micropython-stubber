"""partial used to read the modulelist.txt file"""
from typing import TYPE_CHECKING, List, type_check_only

if TYPE_CHECKING:
    import gc
    import logging

    @type_check_only
    class Stubber:
        path: str
        _report: List[str]
        modules = []

        def __init__(self, path: str = "", firmware_id: str = "") -> None:
            ...

        def clean(self) -> None:
            ...

        def create_one_stub(self, modulename: str) -> bool:
            ...

        def report(self, filename: str = "modules.json"):
            ...

        def create_all_stubs(self):
            ...

    @type_check_only
    def read_path() -> str:
        ...

    def file_exists(f: str) -> bool:
        ...

    @type_check_only
    class _gc:
        def collect(self) -> None:
            ...

    _log = logging.getLogger("stubber")

    # help type checker
    stubber: Stubber = None  # type: ignore
    LIBS: List[str] = [".", "lib"]


# sourcery skip: use-named-expression
###PARTIAL###
# Read stubs from modulelist in the current folder or in /libs
# fall back to default modules
def get_modulelist(stubber):
    # new
    gc.collect()
    stubber.modules = []  # avoid duplicates
    for p in LIBS:
        fname = p + "/modulelist.txt"
        if not file_exists(fname):
            continue
        with open(fname) as f:
            # print("DEBUG: list of modules: " + p + "/modulelist.txt")
            while True:
                line = f.readline().strip()
                if not line:
                    break
                if len(line) > 0 and line[0] != "#":
                    stubber.modules.append(line)
            gc.collect()
            print("BREAK")
            break

    if not stubber.modules:
        stubber.modules = ["micropython"]
        # _log.warn("Could not find modulelist.txt, using default modules")
    gc.collect()


stubber.modules = []  # avoid duplicates
get_modulelist(stubber)
###PARTIALEND###
