"""
This file contains the `def main()` funcion for the db variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""

from io import TextIOWrapper
from typing import TYPE_CHECKING, List, type_check_only

# sourcery skip: require-parameter-annotation
if TYPE_CHECKING:
    import gc
    import logging
    import sys

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

    def read_path() -> str:
        ...

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
        print("Opened existing db")
    except OSError:
        f = open("modulelist.done", "w+b")
        print("created new db")
        was_running = False
    stubber = Stubber(path=read_path())

    # f_name = "{}/{}".format(stubber.path, "modules.json")
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()
    # get list of modules to process
    modules_done = read_done()
    # see if we can continue from where we left off
    get_modulelist(stubber, modules_done)

    if not stubber.modules:
        print("All modules have been processed, exiting")
    else:
        del modules_done
        gc.collect()
        for modulename in stubber.modules:
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
            # modules_done[modulename] = str(stubber._report[-1] if ok else "failed")
            with open("modulelist.done", "a") as f:
                f.write("{}={}\n".format(modulename, "ok" if ok else "failed"))

    # Finished processing - load all the results , and remove the failed ones
    modules_done = read_done()
    if modules_done:
        # stubber.write_json_end(mod_fp)
        stubber._report = []
        for k, v in modules_done.items():
            if v != "failed":
                stubber._report.append('{{"module": "{0}", "file": "{0}.py"}}'.format(k))
        stubber.report()


def read_done():
    modules_done = {}  # type: dict[str, str]
    try:
        with open("modulelist.done") as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                if len(line) > 0 and line[0] != "#":
                    key, value = line.split("=", 1)
                    modules_done[key] = value
    except (OSError, SyntaxError):
        print("could not read modulelist.done")
    finally:
        gc.collect()
        return modules_done


def get_modulelist(stubber, modules_done):
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
                if line and line not in modules_done.keys():
                    stubber.modules.append(line)
            gc.collect()
            print("BREAK")
            break

    if not stubber.modules:
        stubber.modules = ["micropython"]
        # _log.warn("Could not find modulelist.txt, using default modules")
    gc.collect()


###PARTIALEND###
