# type: ignore
"""
This file contains the `def main()` funcion for the db variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""

# sourcery skip: require-parameter-annotation, for-append-to-extend, use-named-expression

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    import gc
    import logging

    class logging:
        def getLogger(self, name: str) -> "logging": ...

        def info(self, msg: str) -> None: ...

    log = logging()

    class Stubber:
        path: str
        _report: List[str]
        modules = []
        _json_name: str

        def __init__(self, path: str = "", firmware_id: str = "") -> None: ...

        def clean(self) -> None: ...

        def create_one_stub(self, modulename: str) -> bool: ...

        def report_start(self, filename: str = "modules.json"): ...

        def report_end(self): ...

        def create_all_stubs(self): ...

    def read_path() -> str: ...

    class _gc:
        def collect(self) -> None: ...

    gc: _gc
    log = logging.getLogger("stubber")

    def file_exists(filename: str) -> bool: ...

    LIBS = [".", "lib"]


###PARTIAL###
SKIP_FILE = "modulelist.done"


def get_modules(skip=0):
    # new
    for p in LIBS:
        fname = p + "/modulelist.txt"
        if not file_exists(fname):
            continue
        try:
            with open(fname) as f:
                i = 0
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    if len(line) > 0 and line[0] == "#":
                        continue
                    i += 1
                    if i < skip:
                        continue
                    yield line
                break
        except OSError:
            pass


def write_skip(done):
    # write count of modules already processed to file
    with open(SKIP_FILE, "w") as f:
        f.write(str(done) + "\n")


def read_skip():
    # read count of modules already processed from file
    done = 0
    try:
        with open(SKIP_FILE) as f:
            done = int(f.readline().strip())
    except OSError:
        pass
    return done


def main():
    import machine  # type: ignore

    was_running = file_exists(SKIP_FILE)
    if was_running:
        log.info("Continue from last run")
    else:
        log.info("Starting new run")
    # try:
    #     f = open("modulelist.done", "r+b")
    #     was_running = True
    #     print("Continue from last run")
    # except OSError:
    #     f = open("modulelist.done", "w+b")
    #     was_running = False
    stubber = Stubber(path=read_path())

    # f_name = "{}/{}".format(stubber.path, "modules.json")
    skip = 0
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()
        stubber.report_start("modules.json")
    else:
        skip = read_skip()
        stubber._json_name = "{}/{}".format(stubber.path, "modules.json")

    for modulename in get_modules(skip):
        # ------------------------------------
        # do epic shit
        # but sometimes things fail / run out of memory and reboot
        try:
            stubber.create_one_stub(modulename)
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()
        # -------------------------------------
        gc.collect()
        # modules_done[modulename] = str(stubber._report[-1] if ok else "failed")
        # with open("modulelist.done", "a") as f:
        #     f.write("{}={}\n".format(modulename, "ok" if ok else "failed"))
        skip += 1
        write_skip(skip)

    print("All modules have been processed, Finalizing report")
    stubber.report_end()


###PARTIALEND###
