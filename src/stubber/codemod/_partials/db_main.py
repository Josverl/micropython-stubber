"""
This file contains the `def main()` funcion for the db variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""
# sourcery skip: require-parameter-annotation, for-append-to-extend, use-named-expression

from io import TextIOWrapper
from typing import TYPE_CHECKING, List, type_check_only

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

    def file_exists(filename: str) -> bool:
        ...

    LIBS = [".", "lib"]


###PARTIAL###
def get_modules(skip=0):
    # new
    for p in LIBS:
        fname = p + "/modulelist.txt"
        if not file_exists(fname):
            continue
        try:
            with open(fname) as f:
                # print("DEBUG: list of modules: " + p + "/modulelist.txt")
                for _ in range(skip):
                    f.readline()
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    if len(line) > 0 and line[0] != "#":
                        yield line
                break
        except OSError:
            pass


def write_skip(done):
    # write count of modules already processed to file
    with open("modulelist.skip", "w") as f:
        f.write(str(done) + "\n")


def read_skip():
    # read count of modules already processed from file
    done = 0
    try:
        with open("modulelist.skip") as f:
            done = int(f.readline().strip())
    except OSError:
        pass
    return done


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
    skip = 0
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()
    else:
        skip = read_skip()

    for modulename in get_modules(skip):
        # ------------------------------------
        # do epic shit
        # but sometimes things fail / run out of memory and reboot
        ok = False
        try:
            ok = stubber.create_one_stub(modulename)
            stubber._report = []
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()
        # -------------------------------------
        gc.collect()
        # modules_done[modulename] = str(stubber._report[-1] if ok else "failed")
        with open("modulelist.done", "a") as f:
            f.write("{}={}\n".format(modulename, "ok" if ok else "failed"))
        skip += 1
        write_skip(skip)

    print("All modules have been processed, Building Report")
    # Finished processing - load all the results , and remove the failed ones
    modules_done = read_done()
    if modules_done:
        # stubber.write_json_end(mod_fp)
        stubber._report = []
        stubber._report.extend(
            '{{"module": "{0}", "file": "{0}.py"}}'.format(k) for k, v in modules_done.items() if v != "failed"
        )
        stubber.report()


###PARTIALEND###
