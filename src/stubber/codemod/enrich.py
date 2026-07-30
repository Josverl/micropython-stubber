"""
Enrich firmware stubs by copying docstrings and parameter information from doc-stubs or python source code.
Both (.py or .pyi) files are supported.
"""

import hashlib
import re
import shutil
from collections.abc import Generator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union  # noqa: UP035

from libcst import ParserSyntaxError
from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config  # type: ignore
from mpflash.logger import log

import stubber.codemod.merge_docstub as merge_docstub
from stubber.merge_config import CP_REFERENCE_TO_DOCSTUB, copy_type_modules
from stubber.modcat import U_MODULES
from stubber.utils import cache as cache_cfg
from stubber.utils.post import format_stubs

# ---------------------------------------------------------------------------
# Disk cache for the (slow) libcst-based merge transform.
#
# `enrich_file` is called very often, frequently with the *same* source and
# target content, and also repeatedly with a *different* source but the *same*
# target (incremental enrichment). Caching only on the target path is therefore
# not sufficient - the cache key is derived from the *content* of both the
# source and the target file, plus the copy_* flags and the target module name.
#
# Enable/disable via the shared `STUBBER_CACHE` toggle (see stubber.utils.cache).
# ---------------------------------------------------------------------------

# Name of this logical cache under the shared cache directory.
_ENRICH_CACHE = "enrich"

# Bump when the merge logic changes in a way that invalidates cached results.
ENRICH_CACHE_VERSION = "2"

# Sentinel stored when the transform produced no change, so a cached "no change"
# result can be told apart from a cache miss.
_NO_CHANGE = "\x00__enrich_no_change__\x00"

# ---------------------------------------------------------------------------
# Volatile-line masking.
#
# Every MCU stub carries a few lines that differ per board / firmware / stubber
# build but do *not* influence how docstrings and type hints are merged, e.g.:
#
#   # MCU: {'variant': '', 'port': 'esp32', 'board': 'ESP32_GENERIC', ...}
#   # Stubber: v1.28.0
#   Module: 'machine' on micropython-v1.28.0-esp32-ESP32_GENERIC   (in the docstring)
#
# These lines pass through the merge as opaque text. By masking them with a
# stable placeholder *before* hashing and *before* running the transform, stubs
# that differ only in these lines share a single cache entry. The original lines
# are restored in the output afterwards, so the result is byte-identical to an
# unmasked run.
# ---------------------------------------------------------------------------
_VOLATILE_TOKEN = "__ENRICH_VOLATILE_{}__"

# (pattern, placeholder-template). The comment patterns keep a leading `# ` so
# the placeholder stays a valid comment; the docstring pattern replaces the
# whole line (it lives inside a string literal).
_VOLATILE_PATTERNS = (
    (re.compile(r"^# MCU: .*$", re.MULTILINE), "# " + _VOLATILE_TOKEN),
    (re.compile(r"^# Stubber: .*$", re.MULTILINE), "# " + _VOLATILE_TOKEN),
    (re.compile(r"^Module: '.*' on .*$", re.MULTILINE), _VOLATILE_TOKEN),
)


def _mask_volatile(text: str) -> Tuple[str, Dict[str, str]]:
    """Replace per-board volatile lines with stable placeholders.

    Returns the masked text and a mapping of `placeholder -> original line` so the
    original lines can be restored in the transform output.
    """
    restore: Dict[str, str] = {}
    for idx, (pattern, template) in enumerate(_VOLATILE_PATTERNS):
        placeholder = template.format(idx)

        def _sub(match: "re.Match[str]", _ph: str = placeholder) -> str:
            restore[_ph] = match.group(0)
            return _ph

        text = pattern.sub(_sub, text, count=1)
    return text, restore


def _restore_volatile(text: str, restore: Dict[str, str]) -> str:
    """Restore the original volatile lines that `_mask_volatile` replaced."""
    for placeholder, original in restore.items():
        text = text.replace(placeholder, original)
    return text


def _enrich_cache_key(
    source_texts: List[str],
    target_text: str,
    module_name: str,
    copy_params: bool,
    copy_docstr: bool,
    copy_returns: bool,
) -> str:
    """Build a content-based cache key for a merge transform (one or more sources)."""
    h = hashlib.sha256()
    parts = [
        ENRICH_CACHE_VERSION,
        module_name,
        f"{int(copy_params)}{int(copy_docstr)}{int(copy_returns)}",
        str(len(source_texts)),
        *source_texts,
        target_text,
    ]
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _run_merge_transform(
    source_paths: List[Path],
    target_text: str,
    module_name: str,
    filename: str,
    copy_params: bool,
    copy_docstr: bool,
    copy_returns: bool,
) -> Optional[str]:
    """Run the (expensive) libcst merge transform and return the new code, or None.

    All `source_paths` are merged into the target in a single transform pass, which
    avoids re-parsing the (potentially large) target once per source doc-stub.
    """
    config: Dict[str, Any] = _default_config()
    context = CodemodContext(filename=filename, full_module_name=module_name)
    codemod_instance = merge_docstub.MergeCommand(
        context,
        docstub_file=source_paths,
        copy_params=copy_params,
        copy_docstr=copy_docstr,
        copy_returns=copy_returns,
    )
    # Do NOT format here (format_code=False). `enrich_folder` runs `ruff format`
    # (format_stubs) exactly once at the end, so per-file black/ruff formatting
    # would be redundant work. Keeping the transform output unformatted also makes
    # the cached value formatter-independent.
    return exec_transform_with_prettyprint(
        codemod_instance,
        target_text,
        generated_code_marker=config["generated_code_marker"],
        format_code=False,
    )


def _cached_merge_transform(
    source_paths: List[Path],
    target_text: str,
    module_name: str,
    filename: str,
    copy_params: bool,
    copy_docstr: bool,
    copy_returns: bool,
) -> Optional[str]:
    """Run `_run_merge_transform`, transparently caching the result on disk."""
    if not cache_cfg.CACHE_ENABLED:
        return _run_merge_transform(source_paths, target_text, module_name, filename, copy_params, copy_docstr, copy_returns)

    # Mask per-board volatile lines so stubs that differ only in those lines hit
    # the same cache entry; the transform runs on (and caches) the masked text.
    masked_target, restore = _mask_volatile(target_text)
    source_texts = [p.read_text(encoding="utf-8") for p in source_paths]
    key = _enrich_cache_key(source_texts, masked_target, module_name, copy_params, copy_docstr, copy_returns)
    cache = cache_cfg.get_cache(_ENRICH_CACHE)
    cached = cache.get(key, default=None)
    if cached is not None:
        log.trace(f"enrich cache hit for {filename}")
        return None if cached == _NO_CHANGE else _restore_volatile(str(cached), restore)

    new_code = _run_merge_transform(source_paths, masked_target, module_name, filename, copy_params, copy_docstr, copy_returns)
    cache.set(key, new_code if new_code is not None else _NO_CHANGE)
    return _restore_volatile(new_code, restore) if new_code is not None else None


def clear_enrich_cache() -> int:
    """Clear the enrich cache. Returns the number of removed entries."""
    return cache_cfg.clear_cache(_ENRICH_CACHE)


def enrich_cache_stats() -> Dict[str, Any]:
    """Return simple statistics about the enrich cache."""
    return cache_cfg.cache_stats(_ENRICH_CACHE)


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
    source_path: Union[Path, List[Path]],
    target_path: Path,
    diff: bool = False,
    write_back: bool = False,
    # package_name="",  # not used
    copy_params: bool = False,
    copy_docstr: bool = False,
    copy_returns: bool = False,
) -> Generator[str, None, None]:
    """
    Enrich firmware stubs using the doc-stubs in another folder.
    Both (.py or .pyi) files are supported.
    Both source an target files must exist, and are assumed to match.
    Any matching of source and target files should be done before calling this function.

    Parameters:
        source_path: the path (or list of paths) to the doc-stub file(s) to enrich from.
            When several paths are given they are merged into the target in a single pass.
        target_path: the path to the firmware stub-file to enrich
        diff: if True, return the diff between the original and the enriched source file
        write_back: if True, write the enriched source file back to the source_path

    Returns:
    - None or a string containing the diff between the original and the enriched source file
    """
    source_paths = [source_path] if isinstance(source_path, Path) else list(source_path)

    if not source_paths or not target_path.exists():
        raise FileNotFoundError("Source or target file not found")
    if not all(p.exists() for p in source_paths):
        raise FileNotFoundError("Source or target file not found")
    if not all(p.is_file() for p in source_paths) or not target_path.is_file():
        raise FileNotFoundError("Source or target is not a file")
    log.info(f"Enriching file: {target_path}")
    # read target file
    old_code = current_code = target_path.read_text(encoding="utf-8")
    # apply the codemod to the target file (transparently cached on disk)
    new_code = _cached_merge_transform(
        source_paths,
        current_code,
        module_name=package_from_path(target_path),
        filename=target_path.as_posix(),
        copy_params=copy_params,
        copy_docstr=copy_docstr,
        copy_returns=copy_returns,
    )
    if new_code:
        current_code = new_code

    if not new_code:
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
    copy_returns: bool = False,
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

    # Group all matching doc-stubs per target so each (potentially large) target is
    # parsed and transformed only once, merging all its sources in a single pass.
    # This avoids re-parsing e.g. machine.pyi once per machine/*.pyi doc-stub.
    sources_by_target: Dict[Path, List[Path]] = {}
    for mm in candidates:
        sources_by_target.setdefault(mm.target, []).append(mm.source)

    # sort by target (stable diffs) and sources per target (stable cache keys)
    reported_errors: set = set()
    errors: List[Exception] = []
    for target in sorted(sources_by_target):
        sources = sorted(sources_by_target[target])
        try:
            log.debug(f"Enriching {target}")
            for s in sources:
                log.debug(f"     from {s}")
            if diff := list(
                enrich_file(
                    sources,
                    target,
                    diff=True,
                    write_back=write_back,
                    # package_name=mm.target_pkg,
                    copy_params=copy_params,
                    copy_docstr=copy_docstr,
                    copy_returns=copy_returns,
                )
            ):
                count += len(diff)
                if show_diff:
                    for d in diff:
                        print(d)
        except FileNotFoundError as e:
            # no docstub to enrich with
            if require_docstub:
                raise (FileNotFoundError(f"No doc-stub or source  file found for {target}")) from e
        except (Exception, ParserSyntaxError) as e:
            errors.append(e)
            # A malformed *source* doc-stub can affect many boards; report each
            # distinct parse error once (concisely) instead of a full traceback
            # for every affected target.
            first_line = next((ln for ln in str(e).splitlines() if ln.strip()), repr(e))
            if first_line not in reported_errors:
                reported_errors.add(first_line)
                log.warning(f"Skipped enriching (parse error): {first_line}")
            continue

    if errors:
        raise ValueError(f"Failed to enrich {len(errors)} file(s); first error: {errors[0]}") from errors[0]

    # run ruff on the target folder
    format_stubs(target_folder)
    # DO NOT run Autoflake as this removes some relevant (but unused) imports too early

    # if copy_params:
    #     copy_type_modules(source_folder, target_folder, CP_REFERENCE_TO_DOCSTUB)

    # report how well the enrich cache performed for this run.
    # NOTE: logged at debug level - `enrich_folder` is often called in a loop
    # (e.g. once per board in `get-frozen`), so the cumulative stats would spam
    # the info log if reported at info level.
    if cache_cfg.CACHE_ENABLED:
        stats = enrich_cache_stats()
        log.debug(f"enrich cache: {stats['hits']} hits, {stats['misses']} misses, {stats['size']} entries in {stats['directory']}")
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
