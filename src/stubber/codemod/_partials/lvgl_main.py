"""
This file contains the `def main()` funcion for the lvgl variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""
from typing import TYPE_CHECKING, List, type_check_only

if TYPE_CHECKING:
    import sys
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

    @type_check_only
    class _gc:
        def collect(self) -> None:
            ...

    gc: _gc
    _log = logging.getLogger("stubber")


###PARTIAL###
def main():
    try:
        import lvgl  # type: ignore
    except Exception:
        print("\n\nNOTE: The `lvgl` module could not be found on this firmware\n\n")
        return
    # Specify firmware name & version
    fw_id = "lvgl"
    try:
        fw_id = "lvgl-{0}_{1}_{2}-{3}-{4}".format(
            lvgl.version_major(),
            lvgl.version_minor(),
            lvgl.version_patch(),
            lvgl.version_info(),
            sys.platform,
        )
    except Exception:
        fw_id = "lvgl-{0}_{1}_{2}_{3}-{4}".format(8, 1, 0, "dev", sys.platform)
    finally:
        stubber = Stubber(firmware_id=fw_id) # type: ignore
    stubber.clean()
    # modules to stub : only lvgl specifics
    stubber.modules = ["io", "lodepng", "rtch", "lvgl"]  # spell-checker: enable

    gc.collect() # type: ignore

    stubber.create_all_stubs()
    stubber.report()


###PARTIALEND###
