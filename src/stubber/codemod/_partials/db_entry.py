from typing import TYPE_CHECKING, type_check_only

if TYPE_CHECKING:
    from logging import Logger

    @type_check_only
    class Stubber:
        path: str

    @type_check_only
    def read_path() -> str: ...

    @type_check_only
    class _gc():
        def collect(self) -> None:


    gc: _gc
    _log: Logger



###PARTIAL###
def main():
    import machine  # type: ignore

    try:
        f = open("modulelist" + ".done", "r+b")
        was_running = True
        _log.info("Opened existing db")
    except OSError:
        f = open("modulelist" + ".done", "w+b")
        _log.info("created new db")
        was_running = False

    stubber = Stubber(path=read_path())
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()

    # get list of modules to process
    with open("modulelist" + ".txt") as f:
        # not optimal , but works on mpremote and esp8266
        modules = [l.strip() for l in f.read().split("\\n") if len(l.strip()) and l.strip()[0] != "#"]
    gc.collect()
    # remove the ones that are already done
    modules_done = {}  # type: dict[str, str]
    try:
        with open("modulelist" + ".done") as f:
            # not optimal , but works on mpremote and esp8266
            for line in f.read().split("\\n"):
                line = line.strip()
                gc.collect()
                if len(line) > 0:
                    key, value = line.split("=", 1)
                    modules_done[key] = value

    except (OSError, SyntaxError):
        pass

    gc.collect()
    modules = [m for m in modules if m not in modules_done.keys()]
    gc.collect()

    for modulename in modules:
        # ------------------------------------
        # do epic shit
        # but sometimes things fail
        ok = False
        try:
            ok = stubber.create_one_stub(modulename)
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()

        # save the (last) result back to the database/result file
        if ok:
            result = stubber._report[-1]
        else:
            result = "failed"
        # -------------------------------------
        modules_done[modulename] = str(result)
        with open("modulelist" + ".done", "a") as f:
            f.write("{}={}\n".format(modulename, result))

    # Finished processing - load all the results , and remove the failed ones
    if len(modules_done) > 0:
        stubber._report = [v for k, v in modules_done.items() if v != "failed"]
        stubber.report()
###PARTIALEND###
