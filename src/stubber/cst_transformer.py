from typing import List, Optional, Set, Tuple, Union

import libcst as cst
from libcst import matchers as m

from .cst_helpers import with_added_imports


# matchers
# gen_return_statement_matcher = m.Raise(exc=some_version_of("tornado.gen.Return"))
# gen_return_call_with_args_matcher = m.Raise(exc=m.Call(func=some_version_of("tornado.gen.Return"), args=[m.AtLeastN(n=1)]))
# gen_return_call_matcher = m.Raise(exc=m.Call(func=some_version_of("tornado.gen.Return")))
# gen_return_matcher = gen_return_statement_matcher | gen_return_call_matcher
# gen_sleep_matcher = m.Call(func=some_version_of("gen.sleep"))
# gen_task_matcher = m.Call(func=some_version_of("gen.Task"))
# gen_coroutine_decorator_matcher = m.Decorator(decorator=some_version_of("tornado.gen.coroutine"))
# gen_test_coroutine_decorator = m.Decorator(decorator=some_version_of("tornado.testing.gen_test"))
# coroutine_decorator_matcher = gen_coroutine_decorator_matcher | gen_test_coroutine_decorator
# coroutine_matcher = m.FunctionDef(
#     asynchronous=None,
#     decorators=[m.ZeroOrMore(), coroutine_decorator_matcher, m.ZeroOrMore()],
# )


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


class StubMergeTransformer(cst.CSTTransformer):
    """
    A libcst transformer that merges the type-rich information from a doc-stub into
    a firmware stub.
    The resulting file will contain information from both sources.

    - module docstring - from source

    - function parameters and types - from docstubs
    - function return types - from docstubs
    - function docstrings - from source

    """

    def __init__(self) -> None:
        # todo : read and store function defs from stubs
        self.coroutine_stack: List[bool] = []
        self.required_imports: Set[str] = set()

    # ------------------------------------------------------------------------

    def leave_Module(self, node: cst.Module, updated_node: cst.Module) -> cst.Module:
        # if not self.required_imports:
        #     return updated_node
        # imports = [self.make_simple_package_import(required_import) for required_import in self.required_imports]
        # return with_added_imports(updated_node, imports)

        # todo: merge module docstrings
        new_body = updated_node.body
        return updated_node.with_changes(body=new_body)

    # ------------------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        return True

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:

        # fake reading the stub information
        x = cst.parse_statement("def foo(pin: int, /, limit: int = 100) -> str: ...")  # type: ignore

        assert isinstance(x, cst.FunctionDef)

        # todo: merge function  docstrings
        new_body = updated_node.body

        return updated_node.with_changes(params=x.params, returns=x.returns, body=new_body)

    # ------------------------------------------------------------------------

    # @staticmethod
    # def make_simple_package_import(package: str) -> cst.Import:
    #     assert not "." in package, "this only supports a root package, e.g. 'import os'"
    #     return cst.Import(names=[cst.ImportAlias(name=cst.Name(package))])
