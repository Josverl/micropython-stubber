"""
Enrich MCU stubs by copying docstrings and parameter information from doc-stubs or python source code.
Both (.py or .pyi) files are supported.
"""

from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from libcst import ParserSyntaxError
from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config  # type: ignore
from mpflash.logger import log

import stubber.codemod.merge_docstub as merge_docstub
from stubber.utils.post import run_black
from functools import lru_cache

##########################################################################################
# # log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#########################################################################################


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
            return p.parent.stem
    # check One level up - just in case
    for p in _options:
        if len(list(p.parent.parent.glob("__init__.py*"))) > 0:
            return p.parent.parent.stem
    # then use the filename, unless it is a __**__.py
    for p in _options:
        if p.is_file() and not p.stem.startswith("__"):
            return p.stem
    return ""


def upackage_equal(p1: str, p2: str) -> bool:
    """
    Compare package names, return True if they are equal, ignoring an _ or u-prefix and case
    """
    if p1 and p1[0] in ["u", "_"]:
        p1 = p1[1:]
    if p2 and p2[0] in ["u", "_"]:
        p2 = p2[1:]

    return p1.lower() == p2.lower()


def target_source_candidates(
    target: Path, source: Path, package_name: str = ""
) -> Generator[Tuple[Path, Path, str], None, None]:
    """
    Given a target and source path, return a list of tuples of `(target, source, package name)` that are candidates for merging.
    Goal is to match the target and source files based on the package name, to avoid mismatched merges of docstrings and typehints
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
    for t in targets:
        for s in sources:
            if upackage_equal(package_from_path(t), package_from_path(s)):
                yield (t, s, package_from_path(t))


#########################################################################################
def enrich_file(
    target_path: Path,
    source_path: Path,
    diff: bool = False,
    write_back: bool = False,
    package_name="",
    params_only: bool = False,
) -> Generator[str, None, None]:
    """
    Enrich a MCU stubs using the doc-stubs in another folder.
    Both (.py or .pyi) files are supported.

    Parameters:
        source_path: the path to the firmware stub to enrich
        docstub_path: the path to the folder containing the doc-stubs
        diff: if True, return the diff between the original and the enriched source file
        write_back: if True, write the enriched source file back to the source_path

    Returns:
    - None or a string containing the diff between the original and the enriched source file
    """
    config: Dict[str, Any] = _default_config()
    context = CodemodContext()
    package_name = package_name or package_from_path(target_path, source_path)

    # find a matching doc-stub file in the docstub_path
    # candidates = merge_source_candidates(package_name, source_path)
    candidates = target_source_candidates(target_path, source_path)
    # sort by target_path , to show diffs
    candidates = sorted(candidates, key=lambda x: x[0])

    # try to apply all candidates
    success = False
    current = None
    for target, source, name in candidates:
        if target != current:
            # processing a new file
            if current:
                # write updated code to file
                if write_back:
                    log.trace(f"Write back enriched file {current}")
                    current.write_text(current_code, encoding="utf-8")
                if diff:
                    yield diff_code(old_code, current_code, 5, filename=current.name)
            old_code = current_code = target.read_text(encoding="utf-8")
            current = target
        if source.exists():
            log.info(f"Merge {target} from {source}")
            # read source file
            codemod_instance = merge_docstub.MergeCommand(
                context, docstub_file=source, params_only=params_only
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

    if current:
        # write (last) updated code to file
        if write_back:
            log.trace(f"Write back enriched file {current}")
            current.write_text(current_code, encoding="utf-8")
        if diff:
            yield diff_code(old_code, current_code, 5, filename=current.name)


# def merge_source_candidates(package_name: str, docstub_path: Path) -> List[Path]:
#     """Return a list of candidate files in the docstub path that can be used to enrich the provided package_name."""
#     if docstub_path.is_file():
#         candidates = [docstub_path]
#         return candidates
#     # select from .py and .pyi files
#     candidates: List[Path] = []
#     for ext in [".py", ".pyi"]:
#         candidates.extend(file_package(package_name, docstub_path, ext))
#         if package_name[0].lower() in ["u", "_"]:
#             # also look for candidates without leading u ( usys.py <- sys.py)
#             # also look for candidates without leading _ ( _rp2.py <- rp2.py )
#             candidates.extend(file_package(package_name[1:], docstub_path, ext))
#         else:
#             # also look for candidates with leading u ( sys.py <- usys.py)
#             candidates.extend(file_package("u" + package_name, docstub_path, ext))
#     return candidates


def file_package(name: str, docstub_path: Path, ext: str) -> List[Path]:
    """
    Return a list of candidate files in the docstub path that can be used to enrich the provided package_name.
    package_name can be ufoo, foo, _foo, foo or foo.bar
    """
    candidates: List[Path] = []
    candidates.extend(docstub_path.rglob(name.replace(".", "/") + ext))
    if (docstub_path / name).is_dir():
        candidates.extend(docstub_path.rglob(f"{name}/*{ext}"))
    return candidates


def enrich_folder(
    target_path: Path,
    source_path: Path,
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
    if not target_path.exists():
        raise FileNotFoundError(f"Target {target_path} does not exist")
    if not source_path.exists():
        raise FileNotFoundError(f"Source {source_path} does not exist")
    log.info(f"Enrich folder {target_path}.")
    count = 0
    # list all the .py and .pyi files in/under the source folder
    if target_path.is_file():
        target_files = [target_path]
    else:
        target_files = sorted(
            list(target_path.rglob("**/*.py")) + list(target_path.rglob("**/*.pyi"))
        )
    package_name = package_name or package_from_path(target_path, source_path)
    for source_file in target_files:
        try:
            diffs = list(
                enrich_file(
                    source_file,
                    source_path,
                    diff=True,
                    write_back=write_back,
                    package_name=package_name,
                    params_only=params_only,
                )
            )
            if diffs:
                count += len(diffs)
                if show_diff:
                    for diff in diffs:
                        print(diff)
        except FileNotFoundError as e:
            # no docstub to enrich with
            if require_docstub:
                raise (FileNotFoundError(f"No doc-stub file found for {source_file}")) from e
        except (Exception, ParserSyntaxError) as e:
            log.error(f"Error parsing {source_file}")
            log.exception(e)
            continue
    # run black on the destination folder
    run_black(target_path)
    # DO NOT run Autoflake as this removes some relevant (unused) imports too early

    return count
