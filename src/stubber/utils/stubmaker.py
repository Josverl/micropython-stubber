import sys
from pathlib import Path

import mypy.stubgen as stubgen
from loguru import logger as log
from mypy.errors import CompileError

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


def generate_pyi_from_file(file: Path) -> bool:
    """Generate a .pyi stubfile from a single .py module using mypy/stubgen"""

    sg_opt = STUBGEN_OPT
    # Deal with generator passed in
    assert isinstance(file, Path)

    sg_opt.files = [str(file)]
    sg_opt.output_dir = str(file.parent)
    try:
        log.debug(f"Calling stubgen on {str(file)}")
        # TDOD: Stubgen.generate_stubs does not provide a way to return the errors
        # such as `cannot perform relative import`

        stubgen.generate_stubs(sg_opt)
        return True
    except (Exception, CompileError, SystemExit) as e:
        # the only way to know if an error was encountered by generate_stubs
        # TODO: Extract info from e.code or e.args[0] and add that to the manifest ?
        log.warning(e.args[0])
        return False


def generate_pyi_files(modules_folder: Path) -> bool:
    """
    Generate typeshed files for all scripts in a folder using mypy/stubgen

    Returns: False if one or more files had an issue generating a stub
    """
    # stubgen cannot process folders with duplicate modules ( ie v1.14 and v1.15 )
    # NOTE: FIX 1 add __init__.py to umqtt
    if (modules_folder / "umqtt/robust.py").exists():  # and not (freeze_path / "umqtt" / "__init__.py").exists():
        log.debug(f"add missing : umqtt/__init__.py")
        with open(modules_folder / "umqtt" / "__init__.py", "a") as f:
            f.write("")

    modlist = list(modules_folder.glob("**/modules.json"))
    r = True
    if len(modlist) > 1:
        # try to process each module seperatlely
        for mod_manifest in modlist:
            ## generate fyi files for folder
            r = r and generate_pyi_files(mod_manifest.parent)
        return r
    else:  # one or less module manifests
        ## generate fyi files for folder
        log.debug("::group::[stubgen] running stubgen on {0}".format(modules_folder))

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
            log.debug("::group::[stubgen] Failure on folder, attempt to run stubgen per file")
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
                log.debug(f"no matching py for : {str(pyi)}")

        # now stub the rest
        # note in some cases this will try a file twice
        for py in py_files:
            r = r and generate_pyi_from_file(py)
            # todo: report failures by adding to module manifest
        return r
