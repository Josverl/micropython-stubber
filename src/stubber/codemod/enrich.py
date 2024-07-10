"""
Enrich MCU stubs by copying docstrings and parameter information from doc-stubs or python source code.
Both (.py or .pyi) files are supported.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from libcst import ParserSyntaxError
from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config  # type: ignore
from mpflash.logger import log

import stubber.codemod.merge_docstub as merge_docstub
from stubber.utils.post import run_black

##########################################################################################
# # log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#########################################################################################


def enrich_file(
    target_path: Path,
    docstub_path: Path,
    diff: bool = False,
    write_back: bool = False,
    package_name="",
) -> Optional[str]:
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
    if not package_name:
        package_name = (
            target_path.stem if target_path.stem != "__init__" else target_path.parent.stem
        )

    # find a matching doc-stub file in the docstub_path
    docstub_file = None
    if docstub_path.is_file():
        candidates = [docstub_path]
    else:
        candidates = []
        for ext in [".py", ".pyi"]:
            candidates = list(docstub_path.rglob(package_name + ext))
            if package_name[0].lower() == "u":
                # also look for candidates without leading u ( usys.py <- sys.py)
                candidates += list(docstub_path.rglob(package_name[1:] + ext))
            elif package_name[0] == "_":
                # also look for candidates without leading _ ( _rp2.py <- rp2.py )
                candidates += list(docstub_path.rglob(package_name[1:] + ext))
            else:
                # also look for candidates with leading u ( sys.py <- usys.py)
                candidates += list(docstub_path.rglob("u" + package_name + ext))

    for docstub_file in candidates:
        if docstub_file.exists():
            break
        else:
            docstub_file = None
    if not docstub_file:
        raise FileNotFoundError(f"No doc-stub file found for {target_path}")

    log.debug(f"Merge {target_path} from {docstub_file}")
    # read source file
    old_code = target_path.read_text(encoding="utf-8")

    codemod_instance = merge_docstub.MergeCommand(context, docstub_file=docstub_file)
    if not (
        new_code := exec_transform_with_prettyprint(
            codemod_instance,
            old_code,
            # include_generated=False,
            generated_code_marker=config["generated_code_marker"],
            # format_code=not args.no_format,
            formatter_args=config["formatter"],
            # python_version=args.python_version,
        )
    ):
        return None
    if write_back:
        log.trace(f"Write back enriched file {target_path}")
        # write updated code to file
        target_path.write_text(new_code, encoding="utf-8")
    return diff_code(old_code, new_code, 5, filename=target_path.name) if diff else new_code


def enrich_folder(
    source_path: Path,
    docstub_path: Path,
    show_diff: bool = False,
    write_back: bool = False,
    require_docstub: bool = False,
    package_name: str = "",
) -> int:
    """\
        Enrich a folder with containing MCU stubs using the doc-stubs in another folder.
        
        Returns the number of files enriched.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source {source_path} does not exist")
    if not docstub_path.exists():
        raise FileNotFoundError(f"Docstub {docstub_path} does not exist")
    log.debug(f"Enrich folder {source_path}.")
    count = 0
    # list all the .py and .pyi files in the source folder
    if source_path.is_file():
        source_files = [source_path]
    else:
        source_files = sorted(
            list(source_path.rglob("**/*.py")) + list(source_path.rglob("**/*.pyi"))
        )
    for source_file in source_files:
        try:
            diff = enrich_file(
                source_file,
                docstub_path,
                diff=True,
                write_back=write_back,
                package_name=package_name,
            )
            if diff:
                count += 1
                if show_diff:
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
    run_black(source_path)
    # DO NOT run Autoflake as this removes some relevant (unused) imports

    return count
