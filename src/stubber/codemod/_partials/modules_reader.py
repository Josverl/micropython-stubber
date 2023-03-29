"""partial used to read the modulelist.txt file"""


from typing import TYPE_CHECKING, List, type_check_only

if TYPE_CHECKING:
    import sys
    from logging import Logger

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

    @type_check_only
    class _gc:
        def collect(self) -> None:
            ...

    gc: _gc
    _log: Logger
    stubber = Stubber(path=read_path())


###PARTIAL###
# Read stubs from modulelist in the current folder or in /libs
# fall back to default modules
stubber.modules = ["micropython"]
for p in ["", "/lib"]:
    try:
        with open(p + "modulelist" + ".txt") as f:
            # not optimal , but works on mpremote and eps8266
            stubber.modules = [l.strip() for l in f.read().split("\n") if len(l.strip()) and l.strip()[0] != "#"]
            break
    except OSError:
        pass
###PARTIALEND###
