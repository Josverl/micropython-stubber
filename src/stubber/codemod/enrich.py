from pathlib import Path
from typing import Any, Dict, Optional

from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config  # type: ignore
from loguru import logger as log

# from stubber.codemod.merge_docstub import MergeCommand
import stubber.codemod.merge_docstub as merge_docstub
from stubber.utils.post import run_black

##########################################################################################
# # log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#########################################################################################


def enrich_file(target_path: Path, docstub_path: Path, diff=False, write_back=False) -> Optional[str]:
    """\
    Enrich a firmware stubs using the doc-stubs in another folder.
    Both (.py or .pyi) files are supported.

    Parameters:
        source_path: the path to the firmware stub to enrich
        docstub_path: the path to the folder containg the doc-stubs
        diff: if True, return the diff between the original and the enriched source file
        write_back: if True, write the enriched source file back to the source_path

    Returns:
    - None or a string containing the diff between the original and the enriched source file
    """
    config: Dict[str, Any] = _default_config()
    context = CodemodContext()

    # find a matching doc-stub file in the docstub_path
    docstub_file = None
    candidates = []
    for ext in [".py", ".pyi"]:
        candidates = list(docstub_path.rglob(target_path.stem + ext))
        if target_path.stem[0].lower() == "u":
            # also look for candidates without leading u
            candidates += list(docstub_path.rglob(target_path.stem[1:] + ext))
        else:
            # also look for candidates with leading u
            candidates += list(docstub_path.rglob("u" + target_path.stem + ext))

    for docstub_file in candidates:
        if docstub_file.exists():
            break
        else:
            docstub_file = None
    if docstub_file is None:
        raise FileNotFoundError(f"No doc-stub file found for {target_path}")

    log.debug(f"Merge {target_path} from {docstub_file}")
    # read source file
    oldcode = target_path.read_text()

    codemod_instance = merge_docstub.MergeCommand(context, stub_file=docstub_file)
    newcode = exec_transform_with_prettyprint(
        codemod_instance,
        oldcode,
        # include_generated=False,
        generated_code_marker=config["generated_code_marker"],
        # format_code=not args.no_format,
        formatter_args=config["formatter"],
        # python_version=args.python_version,
    )
    if newcode:
        if write_back:
            log.trace(f"Write back enriched file {target_path}")
            # write updated code to file
            target_path.write_text(newcode, encoding="utf-8")
        if diff:  # pragma: no cover
            return diff_code(oldcode, newcode, 5, filename=target_path.name)
        return newcode
    else:
        return None


def enrich_folder(source_folder: Path, docstub_path: Path, show_diff=False, write_back=False, require_docstub=False) -> int:
    """\
        Enrich a folder with containing firmware stubs using the doc-stubs in another folder.
        
        Returns the number of files enriched.
    """
    count = 0
    # list all the .py and .pyi files in the source folder
    source_files = sorted(list(source_folder.rglob("**/*.py")) + list(source_folder.rglob("**/*.pyi")))
    for source_file in source_files:
        try:
            diff = enrich_file(source_file, docstub_path, diff=True, write_back=write_back)
            if diff:
                count += 1
                if show_diff:
                    print(diff)
        except FileNotFoundError:
            # no docstub to enrich with
            if require_docstub:
                raise (FileNotFoundError(f"No doc-stub file found for {source_file}"))
    # run black on the destination folder
    # no Autoflake as this removes some relevan (unused) imports
    run_black(source_folder)

    return count
