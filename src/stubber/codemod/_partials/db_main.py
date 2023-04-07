"""
This file contains the `def main()` funcion for the db variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""

from io import TextIOWrapper
from typing import TYPE_CHECKING, List, type_check_only

# sourcery skip: require-parameter-annotation
if TYPE_CHECKING:
    import logging
    import sys

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

        def write_json_header(self, f: TextIOWrapper):
            ...

        def write_json_node(self, f: TextIOWrapper, n, first=False):
            ...

        def write_json_end(self, f):
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
    _log = logging.getLogger("stubber")

    LIBS = [".", "lib"]


###PARTIAL###
def main():
    import machine  # type: ignore

    try:
        f = open("modulelist.done", "r+b")
        was_running = True
        _log.info("Opened existing db")
    except OSError:
        f = open("modulelist.done", "w+b")
        _log.info("created new db")
        was_running = False
    stubber = Stubber(path=read_path())

    # f_name = "{}/{}".format(stubber.path, "modules.json")
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()
    # get list of modules to process
    stubber.modules = ["micropython"]
    for p in LIBS:
        try:
            with open(p + "/modulelist.txt") as f:
                print("Debug: list of modules: " + p + "/modulelist.txt")
                stubber.modules = []  # avoid duplicates
                for line in f.read().split("\n"):
                    line = line.strip()
                    if len(line) > 0 and line[0] != "#":
                        stubber.modules.append(line)
                gc.collect()
                break
        except OSError:
            pass
    gc.collect()
    # remove the ones that are already done
    modules_done = {}  # type: dict[str, str]
    try:
        with open("modulelist.done") as f:
            # not optimal , but works on mpremote and esp8266
            for line in f.read().split("\n"):
                line = line.strip()
                gc.collect()
                if len(line) > 0:
                    key, value = line.split("=", 1)
                    modules_done[key] = value
    except (OSError, SyntaxError):
        pass
    gc.collect()
    # see if we can continue from where we left off
    modules = [m for m in stubber.modules if m not in modules_done.keys()]
    gc.collect()
    for modulename in modules:
        # ------------------------------------
        # do epic shit
        # but sometimes things fail / run out of memory and reboot
        ok = False
        try:
            ok = stubber.create_one_stub(modulename)
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()
        # -------------------------------------
        gc.collect()
        modules_done[modulename] = str(stubber._report[-1] if ok else "failed")
        with open("modulelist.done", "a") as f:
            f.write("{}={}\n".format(modulename, "ok" if ok else "failed"))

    # Finished processing - load all the results , and remove the failed ones
    if modules_done:
        # stubber.write_json_end(mod_fp)
        stubber._report = [v for _, v in modules_done.items() if v != "failed"]
        stubber.report()


###PARTIALEND###
