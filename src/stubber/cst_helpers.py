from typing import List, Sequence, Union

import libcst as cst
from libcst import matchers as m


def with_added_imports(
    module_node: cst.Module, import_nodes: Sequence[Union[cst.Import, cst.ImportFrom]]
) -> cst.Module:
    """
    Adds new import `import_node` after the first import in the module `module_node`.
    """
    updated_body: List[Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]] = []
    added_import = False
    for line in module_node.body:
        updated_body.append(line)
        if not added_import and _is_import_line(line):
            for import_node in import_nodes:
                updated_body.append(cst.SimpleStatementLine(body=tuple([import_node])))
            added_import = True

    if not added_import:
        raise RuntimeError("Failed to add imports")

    return module_node.with_changes(body=tuple(updated_body))


def _is_import_line(
    line: Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]
) -> bool:
    return m.matches(line, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()]))

