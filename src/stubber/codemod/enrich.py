"""
Enrich MCU stubs by copying docstrings and parameter information from doc-stubs or python source code.
Both (.py or .pyi) files are supported.
"""

from collections.abc import Generator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple  # noqa: UP035

from libcst import ParserSyntaxError
from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config  # type: ignore
from mpflash.logger import log

import stubber.codemod.merge_docstub as merge_docstub
from stubber.rst.lookup import U_MODULES
from stubber.utils.post import run_black


##########################################################################################
# # log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#########################################################################################
@dataclass
class MergeMatch:
    target: Path
    source: Path
    target_pkg: str
    source_pkg: str
    is_match: bool


@lru_cache
def package_from_path(target: Path, source: Optional[Path] = None) -> str:
    """
    Given a target and source path, return the package name based on the path.
    """
    # package = None
    _options = [p for p in [target, source] if p is not None]
    for p in _options:
        if not p.exists():
            raise FileNotFoundError(f"Path {p} does not exist")

    # if either the source or target is a package, use that
    for p in _options:
        if p.is_dir():
            if len(list(p.glob("__init__.py*"))) > 0:
                return p.stem
    # check if there is a __init__.py next to the target
    for p in _options:
        if len(list(p.parent.glob("__init__.py*"))) > 0:
            return f"{p.parent.stem}.{p.stem}"
    # check One level up - just in case
    for p in _options:
        if len(list(p.parent.parent.glob("__init__.py*"))) > 0:
            return f"{p.parent.parent.stem}.{p.parent.stem}.{p.stem}"
    # then use the filename, unless it is a __**__.py
    for p in _options:
        if p.is_file() and not p.stem.startswith("__"):
            return p.stem
    return ""


def upackage_equal(src: str, target: str) -> Tuple[bool, int]:
    """
    Compare package names, return True if they are equal, ignoring an _ or u-prefix and case
    """
    if src.startswith("u") and not target.startswith("u"):
        # do not allow enriching from u-module to module
        return False, 0
    if not src.startswith("u") and target.startswith("u"):
        # allow enriching from module to u-module
        target = target[1:]

    # traet __init__ as a package
    if src.endswith(".__init__"):
        src = src[:-9]
    if target.endswith(".__init__"):
        target = target[:-9]
    #
    if src and src[0] == "_":
        src = src[1:]
    if target and target[0] == "_":
        target = target[1:]

    src = src.lower()
    target = target.lower()

    if src == target or f"u{src}" == target:
        return True, len(src)
    if "." in src and src.startswith(f"{target}."):
        return True, len(target)
    if "." in target and target.startswith(f"{src}."):
        return True, len(src)
    return False, 0


def source_target_candidates(source: Path, target: Path) -> Generator[MergeMatch, None, None]:
    """
    Given a target and source path, return a list of tuples of `(target, source, package name)` that are candidates for merging.
    Goal is to match the target and source files based on the package name, to avoid mismatched merges of docstrings and typehints

    Returns a generator of tuples of `(target, source, target_package, source_package, is_partial_match)`
    """
    # first assumption on targets
    if target.is_dir():
        targets = list(target.glob("**/*.py*"))
    elif target.is_file():
        targets = [target]
    else:
        targets = []

    if source.is_dir():
        sources = list(source.glob("**/*.py*"))
    elif source.is_file():
        sources = [source]
    else:
        sources = []
    # filter down using the package name
    for s in sources:
        is_match: bool = False
        best_match_len = 0
        mm = None
        for t in targets:
            # find the best match
            t_pkg = package_from_path(t)
            s_pkg = package_from_path(s)
            is_match, match_len = upackage_equal(s_pkg, t_pkg)
            if is_match and match_len > best_match_len:
                best_match_len = match_len
                mm = MergeMatch(t, s, t_pkg, s_pkg, is_match)
        if not mm:
            continue
        yield mm


#########################################################################################
def enrich_file(
    source_path: Path,
    target_path: Path,
    diff: bool = False,
    write_back: bool = False,
    package_name="",
    params_only: bool = False,
) -> Generator[str, None, None]:
    """
    Enrich a MCU stubs using the doc-stubs in another folder.
    Both (.py or .pyi) files are supported.
    Both source an target files must exist, and are assumed to match.
    Any matching of source and target files should be done before calling this function.

    Parameters:
        source_path: the  path to the firmware stub-file to enrich
        docstub_path: the path to the file  containing the doc-stubs
        diff: if True, return the diff between the original and the enriched source file
        write_back: if True, write the enriched source file back to the source_path

    Returns:
    - None or a string containing the diff between the original and the enriched source file
    """
    config: Dict[str, Any] = _default_config()
    context = CodemodContext()
    package_name = package_name or package_from_path(target_path, source_path)

    if not source_path.exists() or not target_path.exists():
        raise FileNotFoundError("Source or target file not found")
    if not source_path.is_file() or not target_path.is_file():
        raise FileNotFoundError("Source or target is not a file")
    # apply a single codemod to the target file
    success = False
    # read target file
    old_code = current_code = target_path.read_text(encoding="utf-8")
    # read source file
    codemod_instance = merge_docstub.MergeCommand(
        context, docstub_file=source_path, params_only=params_only
    )
    if new_code := exec_transform_with_prettyprint(
        codemod_instance,
        current_code,
        # include_generated=False,
        generated_code_marker=config["generated_code_marker"],
        # format_code=not args.no_format,
        formatter_args=config["formatter"],
        # python_version=args.python_version,
    ):
        current_code = new_code
        success = True

    if not success:
        raise FileNotFoundError(f"No doc-stub file found for {target_path}")
    if write_back:
        log.trace(f"Write back enriched file {target_path}")
        target_path.write_text(current_code, encoding="utf-8")
    if diff:
        yield diff_code(old_code, current_code, 5, filename=target_path.name)

    log.info(f"Enriched {target_path}")


def enrich_folder(
    source_folder: Path,
    target_folder: Path,
    show_diff: bool = False,
    write_back: bool = False,
    require_docstub: bool = False,
    params_only: bool = False,
    package_name: str = "",
) -> int:
    """\
        Enrich a folder with containing MCU stubs using the doc-stubs in another folder.
        
        Returns the number of files enriched.
    """
    if not target_folder.exists():
        raise FileNotFoundError(f"Target {target_folder} does not exist")
    if not source_folder.exists():
        raise FileNotFoundError(f"Source {source_folder} does not exist")
    log.info(f"Enrich folder {target_folder}.")
    count = 0

    candidates = source_target_candidates(source_folder, target_folder)
    # sort by target_path , to show diffs
    candidates = sorted(candidates, key=lambda m: m.target)

    # CHECK: is this still needed?
    # package_name = package_name or package_from_path(target_folder, source_folder)

    # for target in target_files:
    for mm in candidates:
        if mm.target.stem.startswith("u") and mm.target.stem[1:] in U_MODULES:
            # skip enriching umodule.pyi files
            log.debug(f"Skip enriching {mm.target.name}, as it is an u-module")
            continue
        try:

            if diff := enrich_file(
                mm.source,
                mm.target,
                diff=True,
                write_back=write_back,
                package_name=mm.target_pkg,
                params_only=params_only,
            ):
                count += 1
                if show_diff:
                    print(diff)
        except FileNotFoundError as e:
            # no docstub to enrich with
            if require_docstub:
                raise (
                    FileNotFoundError(f"No doc-stub or source  file found for {mm.target}")
                ) from e
        except (Exception, ParserSyntaxError) as e:
            log.error(f"Error parsing {mm.target}")
            log.exception(e)
            continue
    # run black on the target folder
    run_black(target_folder)
    # DO NOT run Autoflake as this removes some relevant (but unused) imports too early

    return count
