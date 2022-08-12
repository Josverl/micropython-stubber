import logging
from pathlib import Path
from typing import Any, Dict, Optional

from libcst.codemod import CodemodContext, diff_code, exec_transform_with_prettyprint
from libcst.tool import _default_config

# from stubber.codemod.merge_docstub import MergeCommand
import stubber.codemod.merge_docstub as merge_docstub

##########################################################################################
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
#########################################################################################


def enrich_sourcefile(source_path: Path, docstub_path: Path, show_diff=False, write_back=False) -> Optional[str]:
    """Enrich a firmware stubs using the doc-stubs in another folder."""
    config: Dict[str, Any] = _default_config()
    context = CodemodContext()

    # find a matching doc-stub file in the docstub_path
    docstub_file = None
    for ext in [".py", ".pyi"]:
        docstub_file = docstub_path / (source_path.stem + ext)
        if docstub_file.exists():
            break
        else:
            docstub_file = None
    if docstub_file is None:
        raise FileNotFoundError(f"No doc-stub file found for {source_path}")

    log.info(f"Enriching {source_path} with {docstub_file}")
    # read source file
    oldcode = source_path.read_text()

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
        if show_diff:

            print(diff_code(oldcode, newcode, 5, filename=source_path.name))
        if write_back:
            # write updated code to file
            source_path.write_text(newcode)
        return newcode
    else:
        return None


def enrich_folder(source_folder: Path, docstub_path: Path, show_diff=False, write_back=False, require_docsub=False) -> int:
    """\
        Enrich a folder with containing firmware stubs using the doc-stubs in another folder.
        
        Returns the number of files enriched.
    """
    count = 0
    # list all the .py and .pyi files in the source folder
    source_files = sorted(list(source_folder.glob("**/*.py")) + list(source_folder.glob("**/*.pyi")))
    for source_file in source_files:
        try:
            enrich_sourcefile(source_file, docstub_path, show_diff)
            count += 1
        except FileNotFoundError:
            # no docstub to enrich with
            if require_docsub:
                raise (FileNotFoundError(f"No doc-stub file found for {source_file}"))
    return count
