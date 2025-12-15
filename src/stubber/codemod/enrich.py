"""
Enrich firmware stubs by copying docstrings and parameter information from doc-stubs or python source code.
Both (.py or .pyi) files are supported.
"""

import shutil
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
from stubber.merge_config import CP_REFERENCE_TO_DOCSTUB, copy_type_modules
from stubber.modcat import U_MODULES
from stubber.utils.post import format_stubs


@dataclass
class MergeMatch:
    """A match between a target and source file to merge docstrings and typehints"""

    target: Path
    source: Path
    target_pkg: str
    source_pkg: str
    is_match: bool


@lru_cache(maxsize=2500)
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
        if p.is_dir() and list(p.glob("__init__.py*")):
            return p.stem

    # check if there is a __init__.py next to the target
    for p in _options:
        if list(p.parent.glob("__init__.py*")):
            return f"{p.parent.stem}.{p.stem}"
    # check One level up - just in case
    for p in _options:
        if list(p.parent.parent.glob("__init__.py*")):
            return f"{p.parent.parent.stem}.{p.parent.stem}.{p.stem}"
    # then use the filename, unless it is a __**__.py
    return next(
        (p.stem for p in _options if p.is_file() and not p.stem.startswith("__")),
        "",
    )


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
    # first check for exact match
    if src == target or f"u{src}" == target:
        return True, len(src)

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


def source_target_candidates(
    source: Path,
    target: Path,
    ext: Optional[str] = None,
) -> Generator[MergeMatch, None, None]:
    """
    Given a target and source path, return a list of tuples of `(target, source, package name)` that are candidates for merging.
    Goal is to match the target and source files based on the package name, to avoid mismatched merges of docstrings and typehints

    Returns a generator of tuples of `(target, source, target_package, source_package, is_partial_match)`
    """
    ext = ext or ".py*"
    # first assumption on targets
    if target.is_dir():
        targets = list(target.glob(f"**/*{ext}"))
    elif target.is_file():
        targets = [target]
    else:
        targets = []

    if source.is_dir():
        sources = list(source.glob(f"**/*{ext}"))
    elif source.is_file():
        sources = [source]
    else:
        sources = []
    # filter down using the package name
    for s in sources:
        is_match: bool = False
        best_match_len = 0
        mm = None
        s_pkg = package_from_path(s)
        for t in targets:
            # find the best match
            if t.stem.startswith("u") and t.stem[1:] in U_MODULES:
                # skip enriching umodule.pyi files
                # log.trace(f"Skip enriching {t.name}, as it is an u-module")
                continue
            t_pkg = package_from_path(t)
            is_match, match_len = upackage_equal(s_pkg, t_pkg)
            if "_mpy_shed" in str(s) or "_mpy_shed" in str(t):
                log.trace(f"Skip _mpy_shed file {s}")
                continue
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
    # package_name="",  # not used
    copy_params: bool = False,
    copy_docstr: bool = False,
) -> Generator[str, None, None]:
    """
    Enrich firmware stubs using the doc-stubs in another folder.
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

    if not source_path.exists() or not target_path.exists():
        raise FileNotFoundError("Source or target file not found")
    if not source_path.is_file() or not target_path.is_file():
        raise FileNotFoundError("Source or target is not a file")
    log.info(f"Enriching file: {target_path}")
    config: Dict[str, Any] = _default_config()
    # fass the filename and module name to the codemod
    context = CodemodContext(
        filename=target_path.as_posix(),
        full_module_name=package_from_path(target_path),
    )
    # apply a single codemod to the target file
    success = False
    # read target file
    old_code = current_code = target_path.read_text(encoding="utf-8")
    # read source file
    codemod_instance = merge_docstub.MergeCommand(
        context,
        docstub_file=source_path,
        copy_params=copy_params,
        copy_docstr=copy_docstr,
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
        yield diff_code(old_code, current_code, 2, filename=target_path.name)


def merge_candidates(
    source_folder: Path,
    target_folder: Path,
) -> List[MergeMatch]:
    """
    Generate a list of merge candidates for the source and target folders.
    Each target is matched with exactly one source file.
    """
    candidates = list(source_target_candidates(source_folder, target_folder))

    # Create a list of candidate matches for the same target
    target_dict = {}
    for candidate in candidates:
        if candidate.target not in target_dict:
            target_dict[candidate.target] = []
        target_dict[candidate.target].append(candidate)

    # first get targets with only one candidate
    candidates = [v[0] for k, v in target_dict.items() if len(v) == 1]

    # then get the best matching from the d
    multiple_candidates = {k: v for k, v in target_dict.items() if len(v) > 1}
    for target in multiple_candidates.keys():
        # if simple module --> complex module : select the best matching or first source
        perfect = next(
            (match for match in multiple_candidates[target] if match.target_pkg == match.source_pkg),
            None,
        )

        if perfect:
            candidates.append(perfect)
        else:
            close_enough = [match for match in multiple_candidates[target] if match.source_pkg.startswith(f"{match.target_pkg}.")]
            if close_enough:
                candidates.extend(close_enough)
            # else:
            #     # take the first one
            #     candidates.append(multiple_candidates[target][0])

    # sort by target_path , to show diffs
    candidates = sorted(candidates, key=lambda m: m.target)
    return candidates


def enrich_folder(
    source_folder: Path,
    target_folder: Path,
    show_diff: bool = False,
    write_back: bool = False,
    require_docstub: bool = False,
    copy_params: bool = False,
    ext: Optional[str] = None,
    copy_docstr: bool = False,
    # package_name: str = "",
) -> int:
    """\
        Enrich a folder containing firmware stubs using the doc-stubs in another folder.
        
        Returns the number of files enriched.
    """
    if not target_folder.exists():
        raise FileNotFoundError(f"Target {target_folder} does not exist")
    if not source_folder.exists():
        raise FileNotFoundError(f"Source {source_folder} does not exist")
    ext = ext or ".py*"
    log.info(f"Enriching from {source_folder} to {target_folder}/**/*{ext}")
    count = 0

    candidates = source_target_candidates(source_folder, target_folder, ext)
    # sort by target_path , to show diffs
    candidates = sorted(candidates, key=lambda m: m.target)

    # for target in target_files:
    for mm in candidates:
        try:
            log.debug(f"Enriching {mm.target}")
            log.debug(f"     from {mm.source}")
            if diff := list(
                enrich_file(
                    mm.source,
                    mm.target,
                    diff=True,
                    write_back=write_back,
                    # package_name=mm.target_pkg,
                    copy_params=copy_params,
                    copy_docstr=copy_docstr,
                )
            ):
                count += len(diff)
                if show_diff:
                    for d in diff:
                        print(d)
        except FileNotFoundError as e:
            # no docstub to enrich with
            if require_docstub:
                raise (FileNotFoundError(f"No doc-stub or source  file found for {mm.target}")) from e
        except (Exception, ParserSyntaxError) as e:
            log.error(f"Error parsing {mm.target}")
            log.exception(e)
            continue

    # run ruff on the target folder
    format_stubs(target_folder)
    # DO NOT run Autoflake as this removes some relevant (but unused) imports too early

    # if copy_params:
    #     copy_type_modules(source_folder, target_folder, CP_REFERENCE_TO_DOCSTUB)
    return count


def guess_port_from_path(folder: Path) -> str:
    """
    Guess the port name from the folder contents.
    ( could also be done based on the path name)

    """
    for port in ["esp32", "samd", "rp2", "pyb"]:
        if (folder / port).exists() or (folder / f"{port}.pyi").exists():
            if port == "pyb":
                return "stm32"
            return port

    if (folder / "esp").exists() or (folder / f"esp.pyi").exists():
        return "esp8266"

    return ""
