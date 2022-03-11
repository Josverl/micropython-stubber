import logging
import shutil

from pathlib import Path
from .. import __version__

import mypy.stubgen as stubgen
from mypy.errors import CompileError
import sys


log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


# default stubgen options
STUBGEN_OPT = stubgen.Options(
    pyversion=(3, 8),  # documentation uses position-only argument indicator which requires 3.8 or higher
    no_import=False,
    include_private=True,
    doc_dir="",
    search_path=[],
    interpreter=sys.executable,
    parse_only=False,
    ignore_errors=True,
    modules=[],
    packages=[],
    files=[],
    output_dir="",
    verbose=True,
    quiet=False,
    export_less=False,
)


def cleanup(modules_folder: Path, all_pyi: bool = False):
    "Q&D cleanup"
    # for some reason (?) the umqtt simple.pyi and robust.pyi are created twice
    #  - modules_root folder ( simple.pyi and robust.pyi) - NOT OK
    #       - umqtt folder (simple.py & pyi and robust.py & pyi) OK
    #  similar for mpy 1.9x - 1.11
    #       - core.pyi          - uasyncio\core.py'
    #       - urequests.pyi     - urllib\urequest.py'
    # Mpy 1.13+
    #       - uasyncio.pyi      -uasyncio\__init__.py

    if all_pyi:
        for file in modules_folder.rglob("*.pyi"):
            file.unlink()
        # no need to remove anything else
        return

    for file_name in (
        "simple.pyi",
        "robust.pyi",
        "core.pyi",
        "urequest.pyi",
        "uasyncio.pyi",
    ):
        f = Path.joinpath(modules_folder, file_name)
        if f.exists():
            try:
                print(" - removing {}".format(f))
                f.unlink()
            except OSError:
                log.error(" * Unable to remove extranous stub {}".format(f))


def generate_pyi_from_file(file: Path) -> bool:
    """Generate a .pyi stubfile from a single .py module using mypy/stubgen"""

    sg_opt = STUBGEN_OPT
    # Deal with generator passed in
    if not isinstance(file, Path):
        raise TypeError
    sg_opt.files = [str(file)]
    sg_opt.output_dir = str(file.parent)
    try:
        print(f"Calling stubgen on {str(file)}")
        # TDOD: Stubgen.generate_stubs does not provide a way to return the errors
        # such as `cannot perform relative import`

        stubgen.generate_stubs(sg_opt)
        return True
    except (Exception, CompileError, SystemExit) as e:
        # the only way to know if an error was encountered by generate_stubs
        # TODO: Extract info from e.code or e.args[0] and add that to the manifest ?
        log.warning(e.args[0])
        return False


def fix_umqtt_init(modules_path: Path):
    # micropython-lib: robust.py needs __init__ to do a relative import
    init_p = modules_path / "umqtt" / "__init__.py"
    if (modules_path / "umqtt").exists() and not init_p.exists():
        with open(init_p, "a") as init:
            init.writelines(
                [
                    "# force __init__.py\n",
                    "pass\n",
                ]
            )


def generate_pyi_files(modules_folder: Path) -> bool:
    """generate typeshed files for all scripts in a folder using mypy/stubgen"""
    # stubgen cannot process folders with duplicate modules ( ie v1.14 and v1.15 )

    modlist = list(modules_folder.glob("**/modules.json"))
    if len(modlist) > 1:
        # try to process each module seperatlely
        r = True
        for mod_manifest in modlist:
            ## generate fyi files for folder
            r = r and generate_pyi_files(mod_manifest.parent)
        return r
    else:  # one or less module manifests
        ## generate fyi files for folder
        # clean before to clean any old stuff
        cleanup(modules_folder, all_pyi=True)
        # fix umqtt/robust issue before it happens
        fix_umqtt_init(modules_folder)
        print("::group::[stubgen] running stubgen on {0}".format(modules_folder))

        Error_Found = False
        sg_opt = STUBGEN_OPT
        sg_opt.files = [str(modules_folder)]
        sg_opt.output_dir = str(modules_folder)
        try:
            stubgen.generate_stubs(sg_opt)
        except (ValueError, SystemExit) as e:
            # the only way to know if an error was encountered by generate_stubs
            # mypy.errors.CompileError and others ?
            # TODO: Extract info from e.code or e.args[0]
            log.warning(e.args[0])
            Error_Found = True

        if Error_Found:
            # in case of failure ( duplicate module in subfolder) then Plan B
            # - run stubgen on each *.py
            print("::group::[stubgen] Failure on folder, attempt to run stubgen per file")
            py_files = list(modules_folder.rglob("*.py"))
            for py in py_files:
                generate_pyi_from_file(py)
                # todo: report failures by adding to module manifest

        # for py missing pyi:
        py_files = list(modules_folder.rglob("*.py"))
        pyi_files = list(modules_folder.rglob("*.pyi"))

        worklist = pyi_files.copy()
        for pyi in worklist:
            # remove all py files that have been stubbed successfully from the list
            try:
                py_files.remove(pyi.with_suffix(".py"))
                pyi_files.remove(pyi)
            except ValueError:
                log.info(f"no matching py for : {str(pyi)}")

        # if there are any pyi files remaining,
        # try to match them to py files and move them to the correct location
        worklist = pyi_files.copy()
        for pyi in worklist:
            match = [py for py in py_files if py.stem == pyi.stem and py.parent.stem == pyi.parent.stem]
            if match:
                # move the .pyi next to the corresponding .py
                log.info(f"moving : {str(pyi)}")
                src = str(pyi)
                dst = str(match[0].with_suffix(".pyi"))
                shutil.move(src, dst)
                try:
                    py_files.remove(match[0])
                    pyi_files.remove(pyi)
                except ValueError:
                    pass

        # now stub the rest
        # note in some cases this will try a file twice
        for py in py_files:
            generate_pyi_from_file(py)
            # todo: report failures by adding to module manifest

        return True
