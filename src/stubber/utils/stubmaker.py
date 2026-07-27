"""Generate stub files for micropython modules using mypy/stubgen"""

import hashlib
import re
import sys
from pathlib import Path

from mpflash.logger import log
import mypy.stubgen as stubgen
from mypy.errors import CompileError

from stubber.utils import cache as cache_cfg

# default stubgen options
STUBGEN_OPT = stubgen.Options(
    pyversion=(
        3,
        8,
    ),  # documentation uses position-only argument indicator which requires 3.8 or higher
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
    inspect=False,  # inspect needs to import the module in CPython, which is not possible for frozen modules
    include_docstrings=True,  # include existing docstrings with the stubs
)

# Logical name of the stubgen cache under the shared cache directory.
_STUBGEN_CACHE = "stubgen"
# Bump when STUBGEN_OPT (options that influence the generated .pyi) changes.
STUBGEN_CACHE_VERSION = "1"


def _stubgen_folder_key(folder: Path) -> str:
    """Content hash of a folder's .py tree (relative path + bytes) -> stubgen cache key.

    Frozen `.py` sources are highly duplicated across ports/boards/versions, so
    identical folder contents map to the same key and can reuse cached .pyi.
    """
    h = hashlib.sha256()
    h.update(STUBGEN_CACHE_VERSION.encode())
    h.update(b"\x00")
    for py in sorted(folder.rglob("*.py")):
        h.update(py.relative_to(folder).as_posix().encode())
        h.update(b"\x00")
        h.update(py.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


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
    if (modules_folder / "umqtt/robust.py").exists():
        log.debug("add missing : umqtt/__init__.py")
        with open(modules_folder / "umqtt" / "__init__.py", "a") as f:
            f.write("")

    # rx_const = re.compile(r"const\(([\w_\"']+)\)")
    rx_const = re.compile(r"const\(([-*<.,:/\(\) \w_\"']+)\)")
    # FIX 2 - replace `const(foo)` with `foo`
    for f in modules_folder.rglob("*.py"):
        if f.is_file():
            with open(f, "r") as file:
                data = file.read()
            original = data
            # regex Search for const\(([\w_"']+)\) and replace with (\1)
            if rx_const.search(data):
                log.debug(f"replace const() in {f}")
                data = rx_const.sub(r"\1", data)
            # TEMPORARY FIX 3 - escape the invalid `"\Z"` escape sequence (e.g. in the
            # frozen fnmatch.py) as `"\\Z"` so the module can be parsed/processed
            # without a SyntaxWarning. Behaviour is unchanged: both are the two
            # characters `\` `Z`. The doubled `"\\Z"` form is left untouched.
            if '"\\Z"' in data:
                log.debug(f'escape invalid "\\Z" sequence in {f}')
                data = data.replace('"\\Z"', '"\\\\Z"')
            # TEMPORARY FIX 4 - escape the invalid `\]` escape sequence (e.g. in the
            # frozen webassembly `string` module) as `\\]`, for the same reason as
            # FIX 3. The negative lookbehind matches only a lone `\]`; an already
            # doubled `\\]` is left untouched.
            if re.search(r"(?<!\\)\\\]", data):
                log.debug(f"escape invalid \\] sequence in {f}")
                data = re.sub(r"(?<!\\)\\\]", lambda _m: "\\\\]", data)
            if data != original:
                with open(f, "w") as file:
                    file.write(data)

    module_list = list(modules_folder.glob("**/modules.json"))
    r = True
    stubgen_cache_key = None
    if len(module_list) > 1:
        # try to process each module separately
        for mod_manifest in module_list:
            ## generate fyi files for folder
            r = r and generate_pyi_files(mod_manifest.parent)
    else:  # one or less module manifests
        # stubgen cache: identical .py folder content (across boards / ports /
        # versions / re-runs) reuses previously generated .pyi and skips stubgen.
        if cache_cfg.CACHE_ENABLED and list(modules_folder.rglob("*.py")):
            stubgen_cache_key = _stubgen_folder_key(modules_folder)
            cached = cache_cfg.get_cache(_STUBGEN_CACHE).get(stubgen_cache_key, default=None)
            if cached is not None:
                log.debug(f"[stubgen] cache hit for {modules_folder}")
                for rel, content in cached.items():
                    out = modules_folder / rel
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(content, encoding="utf-8")
                return True

        ## generate fyi files for folder
        log.debug("::group::[stubgen] running stubgen on {0}".format(modules_folder))

        run_per_file = False
        sg_opt = STUBGEN_OPT
        sg_opt.files = [str(modules_folder)]
        sg_opt.output_dir = str(modules_folder)
        try:
            stubgen.generate_stubs(sg_opt)
        except (Exception, CompileError, SystemExit) as e:
            if isinstance(e, KeyboardInterrupt):
                raise e
            # the only way to know if an error was encountered by generate_stubs
            # mypy.errors.CompileError and others ?
            # TODO: Extract info from e.code or e.args[0]
            log.warning(e.args[0])
            run_per_file = True

        if run_per_file:
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

        work_list = pyi_files.copy()
        for pyi in work_list:
            # remove all py files that have been stubbed successfully from the list
            try:
                py_files.remove(pyi.with_suffix(".py"))
                pyi_files.remove(pyi)
            except ValueError:
                log.debug(f"no matching py for : {str(pyi)}")

        # note in some cases this will try a file twice - but that is better than failing
        for py in py_files:
            r = r and generate_pyi_from_file(py)
            # todo: report failures by adding to module manifest

    # populate the stubgen cache for this (freshly generated) leaf folder
    if stubgen_cache_key is not None:
        produced = {
            p.relative_to(modules_folder).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(modules_folder.rglob("*.pyi"))
        }
        cache_cfg.get_cache(_STUBGEN_CACHE).set(stubgen_cache_key, produced)

    return r
